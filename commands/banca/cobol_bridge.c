#include <stdio.h>

// Funciones COBOL – los nombres deben coincidir con ENTRY
extern void consultar_saldo(long long *saldo);
extern void transferir(long long *saldo, long long *monto);
extern void interes_compuesto(long long *capital, double *tasa, int *periodos);

void c_consultar_saldo(long long *saldo) { consultar_saldo(saldo); }
void c_transferir(long long *saldo, long long *monto) { transferir(saldo, monto); }
void c_interes_compuesto(long long *capital, double *tasa, int *periodos) {
    interes_compuesto(capital, tasa, periodos);
}
