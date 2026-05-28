C     ==================================================================
C     FLUIDSIM.F - TWO-DIMENSIONAL SIMULATION OF FLUID FLOW VELOCITY
C     ==================================================================
      PROGRAM FLUIDSIM
      INTEGER NX, NY, I, J, STEPS
      PARAMETER (NX=10, NY=10)
      REAL U(NX, NY), V(NX, NY), P(NX, NY)
      
C     COMMON BLOCK FOR GLOBAL SYSTEM PARAMETERS
      COMMON /SIMPARAM/ DX, DY, DT, REYNOLDS
      
C     INITIALIZE PHYSICAL PARAMETERS
      DX = 0.1
      DY = 0.1
      DT = 0.01
      REYNOLDS = 100.0
      STEPS = 5
      
C     INITIALIZE GRID VALUES
      DO 20 J = 1, NY
        DO 10 I = 1, NX
          U(I, J) = 1.0
          V(I, J) = 0.0
          P(I, J) = 101.3
10      CONTINUE
20    CONTINUE
      
C     RUN INTERATIVE SOLVER LOOP
      DO 100 I = 1, STEPS
        CALL SOLVER(U, V, P, NX, NY)
100   CONTINUE
      
C     PRINT FINAL RESULTS
      WRITE(*, 9000) U(NX/2, NY/2), V(NX/2, NY/2), P(NX/2, NY/2)
9000  FORMAT('MIDPOINT U:', F8.4, ' V:', F8.4, ' P:', F8.4)
      
      END
      
C     ==================================================================
C     SOLVER SUBROUTINE - UPDATES GRID VALUES BASED ON FINITE DIFFERENCE
C     ==================================================================
      SUBROUTINE SOLVER(U, V, P, NX, NY)
      INTEGER NX, NY, I, J
      REAL U(NX, NY), V(NX, NY), P(NX, NY)
      COMMON /SIMPARAM/ DX, DY, DT, REYNOLDS
      
C     COMPUTE NEXT STEP (SIMPLIFIED PRESSURE CORRECTION)
      DO 200 J = 2, NY - 1
        DO 190 I = 2, NX - 1
          U(I, J) = U(I, J) - DT * (P(I+1, J) - P(I-1, J)) / (2.0 * DX)
          V(I, J) = V(I, J) - DT * (P(I, J+1) - P(I, J-1)) / (2.0 * DY)
190     CONTINUE
200   CONTINUE
      
      RETURN
      END
