class Cliente:
    def __init__(self, nombre: str, telefono: str) -> None:
        self.__nombre = nombre.strip()
        self.__telefono = telefono.strip()
        if not self.__nombre:
            raise ValueError("El nombre del cliente no puede estar vacio.")
        if not self.validar_telefono():
            raise ValueError("El telefono debe tener 8 digitos y empezar con 6 o 7.")
    @property
    def nombre(self) -> str:
        return self.__nombre
    @property
    def telefono(self) -> str:
        return self.__telefono
    def validar_telefono(self) -> bool:
        return (
            len(self.__telefono) == 8
            and self.__telefono.isdigit()
            and self.__telefono[0] in {"6", "7"}
        )