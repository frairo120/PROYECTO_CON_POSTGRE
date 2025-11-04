
from django.core.exceptions import ValidationError


def valida_cedula(value):
    cedula = str(value)

    if not cedula.isdigit():
        raise ValidationError('La cédula debe contener solo números.')

    if len(cedula) != 10:
        raise ValidationError('La cédula debe tener exactamente 10 dígitos.')

    provincia = int(cedula[:2])
    if provincia < 1 or (provincia > 24 and provincia != 30):
        raise ValidationError('El código de provincia en la cédula no es válido.')

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0

    for i in range(9):
        digito = int(cedula[i])
        producto = digito * coeficientes[i]
        if producto > 9:
            producto -= 9
        total += producto

    digito_verificador = (10 - (total % 10)) % 10

    if digito_verificador != int(cedula[9]):
        raise ValidationError('La cédula ingresada no es válida.')

def cedula_valida(cedula):
    """
    Valida una cédula ecuatoriana usando el algoritmo del módulo 10.
    """
    if len(cedula) != 10 or not cedula.isdigit():
        return False

    provincia = int(cedula[:2])
    if provincia < 1 or (provincia > 24 and provincia != 30):
        return False

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0

    for i in range(9):
        mult = int(cedula[i]) * coeficientes[i]
        total += mult - 9 if mult > 9 else mult

    digito_verificador = (10 - total % 10) % 10
    return digito_verificador == int(cedula[9])