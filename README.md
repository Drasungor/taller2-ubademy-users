[![codecov](https://codecov.io/gh/Drasungor/taller2-ubademy-users/branch/main/graph/badge.svg?token=04FUFE05JP)](https://codecov.io/gh/Drasungor/taller2-ubademy-users)

# taller2-ubademy-users

API de Usuarios para el Trabajo Practico de Taller de Programacion 2: Ubademy.

Hecha con FastAPI

### Dependencias
Tener pip instalado.

Instalar las dependencias del proyecto corriendo:
```
pip install -r requirements.txt
```

#### Setup pre-commit
Para instalar los scripts de git hook para el pre-commit, correr:
```
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```
Debería verse el mensaje de éxito que se muestra.
Como paso opcional, se puede corroborar la instalación corriendo pre-commit contra todos los archivos:
```
pre-commit run --all-files
```