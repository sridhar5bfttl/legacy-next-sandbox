#include <iostream>
#include <format>
#include <Eigen/Dense>

// Encapsulation of legacy Fortran COMMON block /SIMPARAM/
struct SimParams {
    double dx;
    double dy;
    double dt;
    double reynolds;
};

// Subroutine SOLVER mapped to a C++ function.
// Matrices are passed by reference and explicitly set to ColMajor to match Fortran memory layout.
void solver(Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor>& U,
            Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor>& V,
            const Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor>& P,
            const SimParams& params) {
    int nx = U.rows();
    int ny = U.cols();
    
    // Fortran loop limits: J = 2 to NY - 1 and I = 2 to NX - 1 (1-indexed)
    // C++ loop limits: j = 1 to ny - 2 and i = 1 to nx - 2 (0-indexed)
    for (int j = 1; j < ny - 1; ++j) {
        for (int i = 1; i < nx - 1; ++i) {
            U(i, j) = U(i, j) - params.dt * (P(i + 1, j) - P(i - 1, j)) / (2.0 * params.dx);
            V(i, j) = V(i, j) - params.dt * (P(i, j + 1) - P(i, j - 1)) / (2.0 * params.dy);
        }
    }
}

int main() {
    // Define parameters matching Fortran's (NX=10, NY=10)
    const int NX = 10;
    const int NY = 10;
    int steps = 5;

    // Column-major matrices matching Fortran's contiguous column storage order
    Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor> U(NX, NY);
    Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor> V(NX, NY);
    Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor> P(NX, NY);

    // Initializing simulation parameters
    SimParams params { 0.1, 0.1, 0.01, 100.0 };

    // Initialize grid values (0-indexed loop equivalents of Fortran loops)
    for (int j = 0; j < NY; ++j) {
        for (int i = 0; i < NX; ++i) {
            U(i, j) = 1.0;
            V(i, j) = 0.0;
            P(i, j) = 101.3;
        }
    }

    // Run iterative solver loops (matches DO 100 I = 1, STEPS)
    for (int step = 0; step < steps; ++step) {
        solver(U, V, P, params);
    }

    // Print final results. Midpoint in Fortran was: U(NX/2, NY/2) -> U(5, 5).
    // In 0-indexed C++, this maps to U(NX/2 - 1, NY/2 - 1) -> U(4, 4)
    std::cout << std::format("MIDPOINT U: {:.4f} V: {:.4f} P: {:.4f}\n", 
                             U(NX/2 - 1, NY/2 - 1), 
                             V(NX/2 - 1, NY/2 - 1), 
                             P(NX/2 - 1, NY/2 - 1));

    return 0;
}
