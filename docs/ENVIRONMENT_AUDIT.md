# Struct3D Environment Audit

## Scope

This document records the environment evidence used by the theory-compliant refactor. It does not redefine the Struct3D theory.

## Historical snapshot

`structure/LogoSP.yml` is retained as a historical environment snapshot. Its exported environment name is `base`, not `LogoSP`, so it is not treated as the canonical Struct3D environment.

The snapshot contains a broad Anaconda/system dependency set, including GUI/OpenGL-related libraries. The package build strings also show `py314` for many packages, indicating that the exported environment is Python 3.14-era. This must be verified locally before using it as a reproduction environment.

## Policy

1. Do not delete or overwrite the historical snapshot during the refactor.
2. Do not claim exact reproducibility from the snapshot alone.
3. Establish a minimal CPU-only Struct3D environment after identifying the actual imports used by the project.
4. Keep environment changes separate from theory changes.
5. Regression results must record Python, NumPy, SciPy, PyTorch, Open3D, scikit-learn, NetworkX, pytest, and CPU/CUDA availability when applicable.

## Current status

- Historical environment snapshot: PRESENT
- Canonical Struct3D environment: NOT YET FROZEN
- Legacy regression baseline: MUST BE RUN IN THE USER'S ACTUAL WORKING ENVIRONMENT
- Theory implementation: NOT changed by this audit

## Next action

Create a dependency manifest from the repository imports and compare it with the historical snapshot. Then run the Energy → Partition → Unit legacy regression suite and record the numerical baseline before modifying any legacy implementation.
