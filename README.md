# FileConverter

Aplicación de escritorio para conversión de archivos (similar a Convertio o iLovePDF), enfocada inicialmente en conversiones **de/hacia PDF** (Word, Excel, PowerPoint, imágenes) y diseñada desde el inicio para ser **escalable a otros tipos de archivo** (audio, video, etc.) sin necesidad de rediseñar el sistema.

La app corre 100% en local: no depende de servicios en la nube ni sube archivos a servidores externos, todo el procesamiento ocurre en la máquina del usuario.

## Idea del proyecto

El usuario abre la app, selecciona o arrastra un archivo, elige el formato de destino, y la app lo convierte usando un motor de conversión en Python que corre como proceso interno (invisible para el usuario). La interfaz está construida en React y empaquetada como aplicación de escritorio con Electron.

Un punto central del diseño es que **agregar un nuevo tipo de conversión no debe requerir tocar el resto del sistema**. Para lograrlo, el backend sigue **arquitectura hexagonal (Ports & Adapters)**, de modo que la lógica de negocio (qué conversiones existen y cómo se orquestan) esté completamente desacoplada de los detalles técnicos (qué librería hace la conversión, si se expone por HTTP o WebSocket, dónde se guardan los archivos temporales, etc.).

## Dos interfaces de usuario

La app incluye **dos versiones de interfaz** intercambiables desde la ventana de opciones (mediante un botón/switch):

- **Modo Básico (SFW)**: misma funcionalidad completa que el modo NSFW, pero con una apariencia sobria y profesional, apta para entornos de trabajo (safe for work).
- **Modo NSFW**: misma funcionalidad, con una apariencia más desinhibida y no apta para entornos laborales (not safe for work).

Ambos modos comparten las mismas capacidades (cola de conversiones, opciones avanzadas, historial, configuración, etc.); solo cambia la capa de presentación visual. La preferencia de modo se persiste entre sesiones.

---

## Arquitectura general

```
┌───────────────────────────────────────────┐
│              Electron (shell)              │
│  ┌───────────────────────────────────────┐ │
│  │     React (Modo Básico / Modo NSFW)     │ │
│  │        UI intercambiable por switch      │ │
│  └────────────────┬────────────────────────┘ │
│                    │ HTTP / WebSocket          │
│  ┌─────────────────▼─────────────────────┐   │
│  │      Backend Python (Hexagonal)         │   │
│  │                                          │   │
│  │   Adaptadores de entrada (HTTP/WS)       │   │
│  │              ↓                           │   │
│  │        Casos de uso (Application)        │   │
│  │              ↓                           │   │
│  │      Dominio (entidades y puertos)       │   │
│  │              ↓                           │   │
│  │   Adaptadores de salida (conversores,    │   │
│  │   almacenamiento temporal, etc.)         │   │
│  └───────────────────────────────────────┘   │
└───────────────────────────────────────────────┘
```

La idea clave de la arquitectura hexagonal: el **dominio** (las reglas de qué es una "conversión" y cómo se valida/orquesta) no sabe nada de FastAPI, ni de PyMuPDF, ni de LibreOffice. Solo conoce **puertos** (interfaces). Los **adaptadores** son los que implementan esos puertos con tecnología concreta, y se pueden reemplazar o agregar sin tocar el dominio.

---

## Lista técnica

### 1. Frontend (UI)
- **React 18+** — librería de UI
- **Vite** — bundler/dev server
- **TailwindCSS** — estilos utilitarios
- **React Dropzone** — manejo de drag & drop de archivos
- **Axios** o `fetch` nativo — llamadas HTTP al backend
- **Zustand** — manejo de estado (progreso, cola de archivos, modo de interfaz activo)
- **React Context API** — control global del modo de interfaz (Básico/NSFW) y su persistencia

### 2. Contenedor Desktop
- **Electron** — ventana nativa + proceso principal
- **electron-builder** — generación de instaladores (.exe, .dmg, .AppImage)
- **electron-store** — persistencia de preferencias del usuario (modo de interfaz, configuración)
- **electron-updater** (futuro) — auto-actualizaciones

### 3. Comunicación Electron ↔ Backend
- **child_process** (Node/Electron) — lanza el ejecutable del backend como proceso hijo
- **get-port** — asigna un puerto libre dinámicamente
- **WebSockets** (`ws` en frontend, soporte nativo de FastAPI) — progreso en tiempo real de conversiones

### 4. Backend — Arquitectura Hexagonal (Ports & Adapters)

**Dominio (`domain/`)**
- Entidades: `ConversionJob`, `FileType`, `ConversionResult`
- Puertos de entrada (input ports): interfaces que definen los casos de uso disponibles (ej. `ConvertFileUseCase`)
- Puertos de salida (output ports): interfaces que el dominio espera que el mundo exterior implemente (ej. `FileConverterPort`, `FileStoragePort`)

**Aplicación (`application/`)**
- Casos de uso que orquestan el dominio: reciben una solicitud de conversión, validan tipos soportados, delegan al adaptador de conversión correspondiente a través de los puertos

**Adaptadores de entrada (`adapters/input/`)**
- **FastAPI** — expone los casos de uso vía HTTP (endpoints tipo `/convert`)
- **Uvicorn** — servidor ASGI
- **python-multipart** — recepción de archivos
- Adaptador WebSocket — reporte de progreso

**Adaptadores de salida (`adapters/output/`)**
- Conversores concretos, cada uno implementando el puerto `FileConverterPort`:
  - **PyMuPDF (fitz)** — PDF ↔ imágenes, manipulación de PDF
  - **pypdf** — merge, split, rotar, metadata
  - **Pillow (PIL)** — conversión entre formatos de imagen
  - **reportlab** — generación de PDFs desde cero
  - **LibreOffice (headless, vía `subprocess`)** — docx/xlsx/pptx/odt → PDF
  - **pdf2docx** (opcional) — PDF → Word editable
  - **ffmpeg** (futuro, vía subprocess o `ffmpeg-python`) — audio/video
- Adaptador de almacenamiento temporal (`tempfile`, `pathlib`)

**Infraestructura (`infrastructure/`)**
- Configuración (`python-dotenv`)
- Logging (`loguru` o `logging` estándar)
- Punto de entrada `main.py` — wiring de dependencias (qué adaptador concreto se inyecta en cada puerto)

### 5. Empaquetado del Backend
- **PyInstaller** — compila el backend a ejecutable standalone, sin depender de Python instalado en la máquina del usuario

### 6. Utilidades generales
- **python-dotenv**, **loguru**, **tempfile**, **pathlib** (ver detalle en infraestructura)

### 7. Testing
- **pytest** — tests de dominio y casos de uso (sin depender de adaptadores reales, gracias a los puertos se pueden mockear fácilmente)
- **Vitest** o **Jest** — tests del frontend React

### 8. Estilo de código
Todo el código (Python y JavaScript/TypeScript) debe seguir los lineamientos de **Clean Code**: funciones pequeñas, nombres significativos, módulos con una sola responsabilidad.

---

## Estructura de carpetas

```
fileconverter/
├── frontend/
│   ├── src/
│   │   ├── interfaces/
│   │   │   ├── basic/        # Modo Básico
│   │   │   └── nsfw/          # Modo NSFW
│   │   ├── shared/            # componentes y lógica compartida entre ambos modos
│   │   ├── context/            # AppModeContext (switch de interfaz)
│   │   └── services/            # cliente HTTP/WebSocket hacia el backend
│   └── vite.config.js
│
├── backend/
│   ├── domain/
│   │   ├── entities/
│   │   └── ports/
│   │       ├── input/
│   │       └── output/
│   ├── application/
│   │   └── use_cases/
│   ├── adapters/
│   │   ├── input/
│   │   │   ├── http/           # routers FastAPI
│   │   │   └── websocket/
│   │   └── output/
│   │       ├── converters/
│   │       │   ├── pdf_to_image_adapter.py
│   │       │   ├── image_to_pdf_adapter.py
│   │       │   ├── office_to_pdf_adapter.py
│   │       │   └── pdf_to_docx_adapter.py
│   │       └── storage/
│   ├── infrastructure/
│   │   ├── config/
│   │   └── main.py
│   └── tests/
│
├── electron/
│   ├── main.js               # proceso principal, lanza backend y crea ventana
│   └── preload.js
│
└── README.md
```

Agregar un nuevo tipo de conversión implica: crear un nuevo adaptador en `adapters/output/converters/`, implementar el puerto `FileConverterPort`, y registrarlo en el wiring de `infrastructure/main.py`. El dominio y los casos de uso no se modifican.

---

## Contratos de los puertos

A continuación se definen las interfaces (puertos) que conectan el dominio con el resto del sistema. Se expresan como `Protocol`/`ABC` de Python porque el backend está en Python, pero conceptualmente son válidas para cualquier lenguaje.

### Entidades base del dominio

```python
# domain/entities.py
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from uuid import UUID


class FileFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    PNG = "png"
    JPG = "jpg"
    # se extiende aquí a medida que se soportan nuevos formatos


class ConversionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ConversionJob:
    job_id: UUID
    source_path: Path
    source_format: FileFormat
    target_format: FileFormat
    options: dict  # ej. {"quality": "high", "dpi": 300}


@dataclass(frozen=True)
class ConversionResult:
    job_id: UUID
    status: ConversionStatus
    output_path: Path | None
    error_message: str | None = None


@dataclass(frozen=True)
class ConversionProgress:
    job_id: UUID
    percentage: int  # 0-100
    status: ConversionStatus
    message: str | None = None
```

### Puertos de entrada (input ports)

Definen qué casos de uso ofrece el dominio hacia afuera. Los adaptadores de entrada (FastAPI, WebSocket) dependen de estas interfaces, nunca al revés.

```python
# domain/ports/input/convert_file_use_case.py
from abc import ABC, abstractmethod
from domain.entities import ConversionJob, ConversionResult


class ConvertFileUseCase(ABC):
    @abstractmethod
    def execute(self, job: ConversionJob) -> ConversionResult:
        """Ejecuta una conversión de archivo de principio a fin."""
        raise NotImplementedError
```

```python
# domain/ports/input/list_supported_conversions_use_case.py
from abc import ABC, abstractmethod
from domain.entities import FileFormat


class ListSupportedConversionsUseCase(ABC):
    @abstractmethod
    def execute(self) -> dict[FileFormat, list[FileFormat]]:
        """Devuelve un mapa de formato origen -> lista de formatos destino soportados."""
        raise NotImplementedError
```

### Puertos de salida (output ports)

Definen qué necesita el dominio del mundo exterior. Los adaptadores de salida (PyMuPDF, LibreOffice, Pillow, sistema de archivos, WebSocket) implementan estas interfaces.

```python
# domain/ports/output/file_converter_port.py
from abc import ABC, abstractmethod
from pathlib import Path
from domain.entities import FileFormat


class FileConverterPort(ABC):
    @abstractmethod
    def supports(self, source: FileFormat, target: FileFormat) -> bool:
        """Indica si este conversor puede manejar el par origen -> destino."""
        raise NotImplementedError

    @abstractmethod
    def convert(self, source_path: Path, target_path: Path, options: dict) -> None:
        """Convierte el archivo. Lanza ConversionError si falla."""
        raise NotImplementedError
```

```python
# domain/ports/output/converter_registry_port.py
from abc import ABC, abstractmethod
from domain.entities import FileFormat
from domain.ports.output.file_converter_port import FileConverterPort


class ConverterRegistryPort(ABC):
    @abstractmethod
    def get_converter(self, source: FileFormat, target: FileFormat) -> FileConverterPort:
        """Devuelve el adaptador de conversión adecuado, o lanza UnsupportedConversionError."""
        raise NotImplementedError
```

```python
# domain/ports/output/file_storage_port.py
from abc import ABC, abstractmethod
from pathlib import Path
from uuid import UUID


class FileStoragePort(ABC):
    @abstractmethod
    def save_temp_file(self, job_id: UUID, content: bytes, filename: str) -> Path:
        """Guarda el archivo entrante en almacenamiento temporal y devuelve su ruta."""
        raise NotImplementedError

    @abstractmethod
    def get_output_path(self, job_id: UUID, target_format: str) -> Path:
        """Genera la ruta donde se escribirá el archivo convertido."""
        raise NotImplementedError

    @abstractmethod
    def cleanup(self, job_id: UUID) -> None:
        """Elimina los archivos temporales asociados a un job."""
        raise NotImplementedError
```

```python
# domain/ports/output/progress_notifier_port.py
from abc import ABC, abstractmethod
from domain.entities import ConversionProgress


class ProgressNotifierPort(ABC):
    @abstractmethod
    def notify(self, progress: ConversionProgress) -> None:
        """Emite una actualización de progreso (ej. vía WebSocket) hacia el frontend."""
        raise NotImplementedError
```

### Cómo encajan las piezas

- `application/use_cases/convert_file.py` implementa `ConvertFileUseCase`. Recibe por inyección de dependencias un `ConverterRegistryPort`, un `FileStoragePort` y un `ProgressNotifierPort` — no importa de dónde vengan esas implementaciones.
- `adapters/output/converters/pdf_to_image_adapter.py` implementa `FileConverterPort` usando PyMuPDF.
- `adapters/output/converters/office_to_pdf_adapter.py` implementa `FileConverterPort` invocando LibreOffice headless vía `subprocess`.
- `adapters/output/storage/local_file_storage_adapter.py` implementa `FileStoragePort` usando `tempfile`/`pathlib`.
- `adapters/output/notifications/websocket_notifier_adapter.py` implementa `ProgressNotifierPort`.
- `adapters/input/http/conversion_router.py` (FastAPI) recibe la petición HTTP, arma un `ConversionJob` y llama a `ConvertFileUseCase.execute(...)` — no conoce ninguna librería de conversión concreta.

Gracias a esto, los tests de `application/use_cases/` pueden mockear los tres puertos de salida sin necesidad de tener PyMuPDF, LibreOffice, ni un servidor real corriendo.

---

## Próximos pasos
- Levantar el esqueleto de Electron + FastAPI comunicándose entre sí
- Implementar el primer conversor (ej. imagen → PDF) de punta a punta como prueba de la arquitectura
- Definir el manejo de errores (`ConversionError`, `UnsupportedConversionError`) y su traducción a respuestas HTTP
