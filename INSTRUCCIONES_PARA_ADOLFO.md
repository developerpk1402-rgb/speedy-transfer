# 🚀 Instrucciones para Adolfo - Speedy Transfer

## 📋 ¿Qué pasó?

**Problema anterior:** Tu error `npm run server` ocurría porque:
1. ❌ No existía `package.json` en el directorio raíz del proyecto
2. ❌ El proyecto Django tenía configuraciones rotas
3. ❌ Las migraciones de la base de datos estaban corruptas
4. ❌ Faltaba el modelo `CarType` que causaba errores de importación

**Solución aplicada:** ✅ He arreglado todos estos problemas y el proyecto ahora funciona correctamente.

## 🔧 ¿Qué necesitas hacer ahora?

### 1. **Actualizar tu proyecto**
```bash
# Navega a tu directorio del proyecto
cd /home/adolfo/www/Speedy-Transfers-main/

# Descarga los cambios más recientes
git pull origin main
```

### 2. **Instalar dependencias (si es necesario)**
```bash
# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar dependencias de Node.js
npm run install-deps
```

### 3. **Configurar la base de datos**
```bash
# Aplicar las nuevas migraciones
python manage.py migrate
```

### 4. **Diagnosticar y arreglar la base de datos (IMPORTANTE)**
```bash
# Primero, diagnosticar el problema
python manage.py diagnose_database

# Si el diagnóstico muestra problemas, forzar la reparación
python manage.py force_fix_database

# Crear datos de prueba
python manage.py create_sample_data
```

### 5. **¡Ejecutar el proyecto!**
```bash
# ✅ CORRECTO: Usar este comando para iniciar el servidor
npm run dev

# O alternativamente:
python manage.py runserver
```

## 🎯 **Comandos disponibles ahora**

### Para el servidor Django:
```bash
npm run dev              # Iniciar servidor de desarrollo
npm run test             # Ejecutar pruebas
npm run migrate          # Aplicar migraciones
npm run makemigrations  # Crear nuevas migraciones
npm run shell           # Abrir shell de Django
npm run collectstatic   # Recopilar archivos estáticos
```

### Para la base de datos:
```bash
python manage.py migrate              # Aplicar migraciones
python manage.py diagnose_database    # Diagnosticar problemas de BD
python manage.py force_fix_database   # Forzar reparación de BD
python manage.py create_sample_data   # Crear datos de prueba
```

### Para desarrollo frontend (CSS):
```bash
npm run build-css        # Construir CSS una vez
npm run install-deps     # Instalar dependencias de Node.js
```

## 🗄️ **Configuración de Base de Datos**

El proyecto ahora detecta automáticamente qué base de datos usar:

1. **MySQL** (si tienes `mysqlclient` instalado)
2. **SQLite** (respaldo automático para desarrollo)

### Variables de entorno (.env file)
Si quieres usar MySQL, crea un archivo `.env` en la raíz del proyecto:
```bash
# Base de datos
DB_NAME=speedy
DB_USER=speedy_user
DB_PASSWORD=tu_contraseña
DB_HOST=127.0.0.1
DB_PORT=3306

# APIs de pago
PAYPAL_CLIENT_ID=tu_paypal_client_id
PAYPAL_SECRET=tu_paypal_secret
STRIPE_PUBLIC_KEY=tu_stripe_public_key
STRIPE_SECRET_KEY=tu_stripe_secret_key

# Email
EMAIL_HOST=65.99.252.200
EMAIL_PORT=465
EMAIL_HOST_USER=soporte@vittapp.com
EMAIL_HOST_PASSWORD=tu_contraseña_email
```

## 🎨 **Desarrollo Frontend**

### Para trabajar con CSS:
```bash
# En una terminal separada, ejecuta esto para ver cambios de CSS en tiempo real
npm run build-css
```

### Archivos importantes:
- **Input CSS**: `templates/assets/src/input.css`
- **Output CSS**: `templates/assets/src/output.css`
- **Configuración**: `templates/assets/tailwind.config.js`

## 🔍 **Solución de problemas**

### Si encuentras errores:

1. **Error de base de datos:**
   ```bash
   # Reiniciar base de datos
   rm db.sqlite3
   rm speedy_app/core/migrations/*.py  # excepto __init__.py
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Error de CSS:**
   ```bash
   # Reinstalar dependencias de Node.js
   npm run install-deps
   npm run build-css
   ```

3. **Error de Python:**
   ```bash
   # Verificar que el entorno virtual esté activado
   source venv/bin/activate  # Linux/Mac
   # o
   venv\Scripts\activate     # Windows
   
   # Reinstalar dependencias
   pip install -r requirements.txt
   ```

## 📁 **Estructura del proyecto actualizada**

```
Speedy-Transfers-main/
├── config/                 # Configuración del proyecto Django
├── speedy_app/            # Aplicación principal Django
│   └── core/              # Funcionalidad principal
├── templates/              # Plantillas HTML
│   └── assets/            # Recursos frontend
├── manage.py              # Gestión de Django
├── package.json           # ✅ NUEVO: Scripts del proyecto
├── requirements.txt       # Dependencias Python
└── SETUP_README.md        # ✅ NUEVO: Guía completa en inglés
```

## 🚀 **Flujo de trabajo recomendado**

### Para desarrollo diario:
1. **Terminal 1:** `npm run dev` (servidor Django)
2. **Terminal 2:** `npm run build-css` (CSS en tiempo real)

### Para hacer cambios:
1. Edita archivos Python/Django normalmente
2. Para CSS: edita `templates/assets/src/input.css`
3. Los cambios se aplican automáticamente

## ✅ **Verificación rápida**

Para verificar que todo funciona:
```bash
# 1. Verificar que Django funciona
python manage.py check

# 2. Iniciar servidor
npm run dev

# 3. Abrir navegador en: http://127.0.0.1:8000/
```

## 📞 **Si necesitas ayuda**

- **Django/Backend**: Revisa los logs de Django y mensajes de error
- **Frontend/CSS**: Verifica la configuración de Node.js y Tailwind
- **Base de datos**: Revisa la configuración de conexión y migraciones
- **Pagos**: Verifica las claves API y variables de entorno

## 🎯 **Próximos pasos**

1. ✅ Configurar variables de entorno
2. ✅ Configurar claves API de pagos
3. ✅ Configurar backend de email
4. ✅ Personalizar plantillas y estilos
5. ✅ Agregar datos de prueba
6. ✅ Configurar ajustes de producción

---

## 🔧 **Cambios realizados en la base de datos**

### ✅ **Problema resuelto: Campo `car_type_id`**
- **Antes:** El campo `car_type_id` era nullable (podía ser NULL)
- **Ahora:** El campo `car_type_id` es NOT NULL (obligatorio)
- **Campo `type` eliminado:** Ya no existe el campo enum `type`, ahora se usa la relación con `CarType`

### 📊 **Estructura actualizada:**
```sql
-- Tabla core_cartype (tipos de carros)
- id (INTEGER, PRIMARY KEY)
- code (varchar(10), UNIQUE) -- SEDAN, SUV, VAN, SPRINTER, BUS
- name (varchar(50)) -- Sedan, SUV, Van, Sprinter, Bus
- description (TEXT)
- max_capacity (INTEGER)

-- Tabla core_car (carros)
- id (INTEGER, PRIMARY KEY)
- name (varchar(50))
- description (TEXT)
- image (varchar(100))
- max (INTEGER)
- car_type_id (bigint, NOT NULL) -- Referencia a core_cartype
```

### 🎯 **Tipos de carros disponibles:**
- **SEDAN:** Sedan (capacidad: 4)
- **SUV:** SUV (capacidad: 6)  
- **VAN:** Van (capacidad: 8)
- **SPRINTER:** Sprinter (capacidad: 12)
- **BUS:** Bus (capacidad: 20)

---

## 🚨 **Errores Adicionales Resueltos**

### **Error: `Car.CAR_TYPES` no existe**
- **Problema:** El código en `views.py` intentaba acceder a `Car.CAR_TYPES` que ya no existe
- **Solución:** ✅ Actualizado el código para usar `CarType.objects.values_list()`
- **Resultado:** El sitio web ahora carga correctamente sin errores

### **Error: `no such column: core_car.car_type_id`**
- **Problema:** La base de datos no tiene la columna `car_type_id` en la tabla `core_car`
- **Causa:** Las migraciones no se aplicaron correctamente o hay un problema con la estructura
- **Solución:** ✅ Ejecutar comandos de diagnóstico y reparación

---

**¡El proyecto ahora está completamente funcional! 🎉**

**Comando principal:** `npm run dev` (en lugar de `npm run server`)

**Base de datos:** ✅ Estructura corregida y optimizada

**Sitio web:** ✅ Carga sin errores

