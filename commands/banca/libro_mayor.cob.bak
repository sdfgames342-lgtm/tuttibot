       IDENTIFICATION DIVISION.
       PROGRAM-ID. libro_mayor.
       DATA DIVISION.

       LINKAGE SECTION.
      *> Variables que vienen desde C
       01 saldo_cliente       PIC S9(10)V9(2) COMP.
       01 monto_movimiento    PIC S9(10)V9(2) COMP.
       01 tasa_input          PIC V9(3).
       01 periodos_input      PIC 9(4) COMP.

       PROCEDURE DIVISION.

      *> Consultar saldo
       ENTRY "consultar_saldo" USING saldo_cliente.
           GOBACK.

      *> Transferir
       ENTRY "transferir" USING saldo_cliente, monto_movimiento.
           COMPUTE saldo_cliente = saldo_cliente - monto_movimiento
           GOBACK.

      *> Interés compuesto
       ENTRY "interes_compuesto" USING saldo_cliente, tasa_input, periodos_input.
           PERFORM UNTIL periodos_input = 0
               COMPUTE saldo_cliente = saldo_cliente * (1 + tasa_input)
               SUBTRACT 1 FROM periodos_input
           END-PERFORM
           GOBACK.

       END PROGRAM libro_mayor.
