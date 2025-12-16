PRAGMA foreign_keys = ON;

-- ============================
-- 1. UBICACIÓN GEOGRÁFICA
-- ============================
CREATE TABLE Tbl_Pais (
    Id_Pais INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_Pais TEXT NOT NULL,
    FechaAlta_Pais DATE,
    Observ_Pais TEXT
);

CREATE TABLE Tbl_Provincia (
    Id_Provincia INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_Provincia TEXT NOT NULL,
    Id_Pais INTEGER,
    FechaAlta_Provincia DATE,
    Observ_Provincia TEXT,
    FOREIGN KEY (Id_Pais) REFERENCES Tbl_Pais(Id_Pais)
);

CREATE TABLE Tbl_Distrito (
    Id_Distrito INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_Distrito TEXT NOT NULL,
    Id_Provincia INTEGER,
    FechaAlta_Distrito DATE,
    Observ_Distrito TEXT,
    FOREIGN KEY (Id_Provincia) REFERENCES Tbl_Provincia(Id_Provincia)
);

-- ============================
-- 2. LOGIN / SEGURIDAD
-- ============================
CREATE TABLE Tbl_Personal (
    Id_Personal INTEGER PRIMARY KEY AUTOINCREMENT,
    DNI TEXT,
    Nombres TEXT,
    Apellidos TEXT,
    Fecha_Nacimiento DATE,
    Telefono TEXT,
    Direccion TEXT,
    Email_Personal TEXT,
    Id_Distrito INTEGER,
    Id_Provincia INTEGER,
    Id_Pais INTEGER,
    Fecha_Ingreso DATE,
    Activo INTEGER,
    FOREIGN KEY (Id_Distrito) REFERENCES Tbl_Distrito(Id_Distrito),
    FOREIGN KEY (Id_Provincia) REFERENCES Tbl_Provincia(Id_Provincia),
    FOREIGN KEY (Id_Pais) REFERENCES Tbl_Pais(Id_Pais)
);

CREATE TABLE Tbl_Users (
    Id_User INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL UNIQUE,
    Email_Acceso TEXT,
    Password_Hash TEXT NOT NULL,
    Activo INTEGER DEFAULT 1,
    Intentos_Fallidos INTEGER DEFAULT 0,
    Bloqueado INTEGER DEFAULT 0,
    Fecha_Alta DATE,
    Id_Personal INTEGER,
    Id_Role INTEGER,
    FOREIGN KEY (Id_Personal) REFERENCES Tbl_Personal(Id_Personal),
    FOREIGN KEY (Id_Role) REFERENCES Tbl_Roles(Id_Role)
);

CREATE TABLE Tbl_Roles (
    Id_Role INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_Role TEXT NOT NULL,
    Descripcion TEXT
);

CREATE TABLE Tbl_Privilegios (
    Id_Privilegio INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_Privilegio TEXT NOT NULL,
    Descripcion TEXT
);

CREATE TABLE Tbl_User_Role (
    Id_User_Role INTEGER PRIMARY KEY AUTOINCREMENT,
    Id_User INTEGER,
    Id_Role INTEGER,
    FOREIGN KEY (Id_User) REFERENCES Tbl_Users(Id_User),
    FOREIGN KEY (Id_Role) REFERENCES Tbl_Roles(Id_Role)
);

CREATE TABLE Tbl_Role_Privilegio (
    Id_Role_Privilegio INTEGER PRIMARY KEY AUTOINCREMENT,
    Id_Role INTEGER,
    Id_Privilegio INTEGER,
    FOREIGN KEY (Id_Role) REFERENCES Tbl_Roles(Id_Role),
    FOREIGN KEY (Id_Privilegio) REFERENCES Tbl_Privilegios(Id_Privilegio)
);

-- ============================
-- 3. PRODUCTOS + AUXILIARES
-- ============================
CREATE TABLE Tbl_Forma (
    Id_Forma INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_Forma TEXT,
    FechaAlta_Forma DATE,
    Observ_Forma TEXT
);

CREATE TABLE Tbl_Presentacion (
    Id_Presentacion INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_Presentacion TEXT,
    FechaAlta_Presentacion DATE,
    Observ_Presentacion TEXT
);

CREATE TABLE Tbl_Fraccion (
    Id_Fraccion INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_Fraccion TEXT,
    FechaAlta_Fraccion DATE,
    Observ_Fraccion TEXT
);

CREATE TABLE Tbl_Titular (
    Id_Titular INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_Titular TEXT,
    FechaAlta_Titular DATE,
    Observ_Titular TEXT
);

CREATE TABLE Tbl_Fabricante (
    Id_Fabricante INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_Fabricante TEXT,
    FechaAlta_Fabricante DATE,
    Observ_Fabricante TEXT
);

CREATE TABLE Tbl_IFA (
    Id_IFA INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_IFA TEXT,
    FechaAlta_IFA DATE,
    Observ_IFA TEXT
);

CREATE TABLE Tbl_Rubro (
    Id_Rubro INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_Rubro TEXT,
    FechaAlta_Rubro DATE,
    Observ_Rubro TEXT
);

CREATE TABLE Tbl_Situacion (
    Id_Situacion INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_Situacion TEXT,
    FechaAlta_Situacion DATE,
    Observ_Situacion TEXT
);

CREATE TABLE Tbl_Productos (
    Id_Prod INTEGER PRIMARY KEY AUTOINCREMENT,
    Cod_Prod TEXT,
    Nom_Prod TEXT,
    Concentracion_Prod TEXT,
    Id_FormaFarmacologica INTEGER,
    Id_Presentacion INTEGER,
    Id_Fraccion INTEGER,
    RegSanitario_Prod TEXT,
    Id_Titular INTEGER,
    Id_Fabricante INTEGER,
    Id_IFA INTEGER,
    Id_Rubro INTEGER,
    Id_Situacion INTEGER,
    FechaAlta_Prod DATE,
    Observ_Prod TEXT,
    FOREIGN KEY (Id_FormaFarmacologica) REFERENCES Tbl_Forma(Id_Forma),
    FOREIGN KEY (Id_Presentacion) REFERENCES Tbl_Presentacion(Id_Presentacion),
    FOREIGN KEY (Id_Fraccion) REFERENCES Tbl_Fraccion(Id_Fraccion),
    FOREIGN KEY (Id_Titular) REFERENCES Tbl_Titular(Id_Titular),
    FOREIGN KEY (Id_Fabricante) REFERENCES Tbl_Fabricante(Id_Fabricante),
    FOREIGN KEY (Id_IFA) REFERENCES Tbl_IFA(Id_IFA),
    FOREIGN KEY (Id_Rubro) REFERENCES Tbl_Rubro(Id_Rubro),
    FOREIGN KEY (Id_Situacion) REFERENCES Tbl_Situacion(Id_Situacion)
);

-- ============================
-- 4. CLIENTE Y PROVEEDOR
-- ============================
CREATE TABLE Tbl_Cliente (
    Id_Cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    DNI_Cliente TEXT,
    Nom_Cliente TEXT,
    Ape_Cliente TEXT,
    Dir_Cliente TEXT,
    Id_Distrito INTEGER,
    Id_Provincia INTEGER,
    Id_Pais INTEGER,
    Tel_Cliente TEXT,
    Email_Cliente TEXT,
    FechaNac_Cliente DATE,
    FechaAlta_Cliente DATE,
    Observ_Cliente TEXT,
    FOREIGN KEY (Id_Distrito) REFERENCES Tbl_Distrito(Id_Distrito),
    FOREIGN KEY (Id_Provincia) REFERENCES Tbl_Provincia(Id_Provincia),
    FOREIGN KEY (Id_Pais) REFERENCES Tbl_Pais(Id_Pais)
);

CREATE TABLE Tbl_Proveedor (
    Id_Proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
    RUC_Proveedor TEXT,
    Nom_Proveedor TEXT,
    Dir_Proveedor TEXT,
    Id_Distrito INTEGER,
    Id_Provincia INTEGER,
    Id_Pais INTEGER,
    Tel_Proveedor TEXT,
    Email_Proveedor TEXT,
    FechaAlta_Proveedor DATE,
    Observ_Proveedor TEXT,
    Activo INTEGER,
    FOREIGN KEY (Id_Distrito) REFERENCES Tbl_Distrito(Id_Distrito),
    FOREIGN KEY (Id_Provincia) REFERENCES Tbl_Provincia(Id_Provincia),
    FOREIGN KEY (Id_Pais) REFERENCES Tbl_Pais(Id_Pais)
);

-- ============================
-- 5. ALMACÉN + STOCK
-- ============================
CREATE TABLE Tbl_Almacen (
    Id_Almacen INTEGER PRIMARY KEY AUTOINCREMENT,
    Cod_Almacen TEXT,
    Nom_Almacen TEXT,
    Direccion_Almacen TEXT,
    Id_Distrito INTEGER,
    Id_Provincia INTEGER,
    Id_Pais INTEGER,
    Activo INTEGER,
    FechaAlta_Almacen DATE,
    Observ_Almacen TEXT,
    FOREIGN KEY (Id_Distrito) REFERENCES Tbl_Distrito(Id_Distrito),
    FOREIGN KEY (Id_Provincia) REFERENCES Tbl_Provincia(Id_Provincia),
    FOREIGN KEY (Id_Pais) REFERENCES Tbl_Pais(Id_Pais)
);

CREATE TABLE Tbl_Stock (
    Id_Stock INTEGER PRIMARY KEY AUTOINCREMENT,
    Id_Almacen INTEGER,
    Id_Prod INTEGER,
    Lote_Prod TEXT,
    FechaVenc_Prod DATE,
    Cant_Actual REAL,
    FechaUltMov_Stock DATE,
    Observ_Stock TEXT,
    FOREIGN KEY (Id_Almacen) REFERENCES Tbl_Almacen(Id_Almacen),
    FOREIGN KEY (Id_Prod) REFERENCES Tbl_Productos(Id_Prod)
);

-- ============================
-- 6. COMPRAS
-- ============================
CREATE TABLE Tbl_Compra (
    Id_Compra INTEGER PRIMARY KEY AUTOINCREMENT,
    Id_Proveedor INTEGER,
    Id_Almacen INTEGER,
    Fec_Compra DATE,
    FecCompra DATETIME,
    Tipo_Doc_Compra TEXT,
    Serie_Doc_Compra TEXT,
    Nro_Doc_Compra TEXT,
    SubTotal_Compra REAL,
    IGV_Compra REAL,
    Total_Compra REAL,
    Id_User INTEGER,
    Observ_Compra TEXT,
    FOREIGN KEY (Id_Proveedor) REFERENCES Tbl_Proveedor(Id_Proveedor),
    FOREIGN KEY (Id_Almacen) REFERENCES Tbl_Almacen(Id_Almacen),
    FOREIGN KEY (Id_User) REFERENCES Tbl_Users(Id_User)
);

CREATE TABLE Tbl_Compra_Detalle (
    Id_Compra_Detalle INTEGER PRIMARY KEY AUTOINCREMENT,
    Id_Compra INTEGER,
    Id_Prod INTEGER,
    Cant_Compra REAL,
    Costo_Unit_Compra REAL,
    Costo_Total_Compra REAL,
    Lote_Prod TEXT,
    FechaVenc_Prod DATE,
    FOREIGN KEY (Id_Compra) REFERENCES Tbl_Compra(Id_Compra),
    FOREIGN KEY (Id_Prod) REFERENCES Tbl_Productos(Id_Prod)
);

-- ============================
-- 7. VENTAS
-- ============================
CREATE TABLE Tbl_Venta (
    Id_Venta INTEGER PRIMARY KEY AUTOINCREMENT,
    Id_Cliente INTEGER,
    Id_Almacen INTEGER,
    Fec_Venta DATE,
    FecVenta DATETIME,
    Tipo_Doc_Venta TEXT,
    Serie_Doc_Venta TEXT,
    Nro_Doc_Venta TEXT,
    SubTotal_Venta REAL,
    IGV_Venta REAL,
    Total_Venta REAL,
    Id_User INTEGER,
    Observ_Venta TEXT,
    FOREIGN KEY (Id_Cliente) REFERENCES Tbl_Cliente(Id_Cliente),
    FOREIGN KEY (Id_Almacen) REFERENCES Tbl_Almacen(Id_Almacen),
    FOREIGN KEY (Id_User) REFERENCES Tbl_Users(Id_User)
);

CREATE TABLE Tbl_Venta_Detalle (
    Id_Venta_Detalle INTEGER PRIMARY KEY AUTOINCREMENT,
    Id_Venta INTEGER,
    Id_Prod INTEGER,
    Cant_Venta REAL,
    Precio_Unit_Venta REAL,
    Importe_Venta REAL,
    FOREIGN KEY (Id_Venta) REFERENCES Tbl_Venta(Id_Venta),
    FOREIGN KEY (Id_Prod) REFERENCES Tbl_Productos(Id_Prod)
);

-- ============================
-- 8. KARDEX
-- ============================
CREATE TABLE Tbl_Mov_Almacen (
    Id_Mov_Almacen INTEGER PRIMARY KEY AUTOINCREMENT,
    Id_Almacen INTEGER,
    Id_Prod INTEGER,
    Lote_Prod TEXT,
    FechaVenc_Prod DATE,
    Tipo_Mov TEXT,
    Fecha_Mov DATETIME,
    Cant_Entrada REAL,
    Cant_Salida REAL,
    Stock_Saldo REAL,
    Costo_Unitario REAL,
    Costo_Total REAL,
    Id_Doc_Ref INTEGER,
    Tipo_Doc_Ref TEXT,
    Id_User INTEGER,
    Observ_Mov TEXT,
    FOREIGN KEY (Id_Almacen) REFERENCES Tbl_Almacen(Id_Almacen),
    FOREIGN KEY (Id_Prod) REFERENCES Tbl_Productos(Id_Prod),
    FOREIGN KEY (Id_User) REFERENCES Tbl_Users(Id_User)
);

-- ============================
-- 9. CRÉDITOS
-- ============================
CREATE TABLE Tbl_Credito (
    Id_Credito INTEGER PRIMARY KEY AUTOINCREMENT,
    Id_Venta INTEGER,
    Id_Cliente INTEGER,
    Fec_Credito DATE,
    Monto_Credito REAL,
    Saldo_Credito REAL,
    Estado_Credito TEXT,
    FechaAlta_Credito DATE,
    Observ_Credito TEXT,
    FOREIGN KEY (Id_Venta) REFERENCES Tbl_Venta(Id_Venta),
    FOREIGN KEY (Id_Cliente) REFERENCES Tbl_Cliente(Id_Cliente)
);

CREATE TABLE Tbl_Pago_Credito (
    Id_Pago_Credito INTEGER PRIMARY KEY AUTOINCREMENT,
    Id_Credito INTEGER,
    Fec_Pago_Credito DATETIME,
    Monto_Pago_Credito REAL,
    FormaPago_Pago TEXT,
    Id_User INTEGER,
    Id_Caja INTEGER,
    Observ_Pago_Credito TEXT,
    FOREIGN KEY (Id_Credito) REFERENCES Tbl_Credito(Id_Credito),
    FOREIGN KEY (Id_User) REFERENCES Tbl_Users(Id_User),
    FOREIGN KEY (Id_Caja) REFERENCES Tbl_Caja(Id_Caja)
);

-- ============================
-- 10. CAJA
-- ============================
CREATE TABLE Tbl_Caja (
    Id_Caja INTEGER PRIMARY KEY AUTOINCREMENT,
    Cod_Caja TEXT,
    Nom_Caja TEXT,
    Id_Almacen INTEGER,
    Activo INTEGER,
    FechaAlta_Caja DATE,
    Observ_Caja TEXT,
    FOREIGN KEY (Id_Almacen) REFERENCES Tbl_Almacen(Id_Almacen)
);

CREATE TABLE Tbl_Apertura_Caja (
    Id_Apertura_Caja INTEGER PRIMARY KEY AUTOINCREMENT,
    Id_Caja INTEGER,
    Id_User INTEGER,
    FecHora_Apertura DATETIME,
    FecHora_Cierre DATETIME,
    Monto_Apertura REAL,
    Monto_Cierre REAL,
    Estado_Apertura TEXT,
    Observ_Apertura TEXT,
    FOREIGN KEY (Id_Caja) REFERENCES Tbl_Caja(Id_Caja),
    FOREIGN KEY (Id_User) REFERENCES Tbl_Users(Id_User)
);

CREATE TABLE Tbl_Mov_Caja (
    Id_Mov_Caja INTEGER PRIMARY KEY AUTOINCREMENT,
    Id_Apertura_Caja INTEGER,
    FecHora_Mov DATETIME,
    Tipo_Mov_Caja TEXT,
    Origen_Mov_Caja TEXT,
    Id_Ref INTEGER,
    Descripcion_Mov TEXT,
    Monto_Mov_Caja REAL,
    Id_User INTEGER,
    FOREIGN KEY (Id_Apertura_Caja) REFERENCES Tbl_Apertura_Caja(Id_Apertura_Caja),
    FOREIGN KEY (Id_User) REFERENCES Tbl_Users(Id_User)
);

-- ============================
-- 11. TURNOS
-- ============================
CREATE TABLE Tbl_Turno (
    Id_Turno INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom_Turno TEXT,
    HoraIni_Turno TEXT,
    HoraFin_Turno TEXT,
    Activo INTEGER,
    Observ_Turno TEXT
);

CREATE TABLE Tbl_User_Turno (
    Id_User_Turno INTEGER PRIMARY KEY AUTOINCREMENT,
    Id_User INTEGER,
    Id_Turno INTEGER,
    FecIni_Turno DATETIME,
    FecFin_Turno DATETIME,
    Id_Caja INTEGER,
    Id_Almacen INTEGER,
    Observ_User_Turno TEXT,
    FOREIGN KEY (Id_User) REFERENCES Tbl_Users(Id_User),
    FOREIGN KEY (Id_Turno) REFERENCES Tbl_Turno(Id_Turno),
    FOREIGN KEY (Id_Caja) REFERENCES Tbl_Caja(Id_Caja),
    FOREIGN KEY (Id_Almacen) REFERENCES Tbl_Almacen(Id_Almacen)
);
