# Struct3D Mathematical Closure — Structural World Quotient Theorem

## 1. Frozen objects

The upstream chain is

`X -> Gamma(X) -> P* -> U -> R -> W=(U,R,Phi)`.

For every selected block `A in P*`, the frozen Unit is

`U_X(A) = (A,T_X(A))`,

where `T_X(A)` contains the complete sorted geometric coordinate signature.
On the simple-observation domain this theta is strictly injective on geometric
blocks and invariant under observation relabeling.

## 2. World quotient

For a theory-facing Unit `u`, define its quotient key by the observation-derived
theta signature. For legacy Units without that signature, the fallback key is
the finite structural attribute/primitive payload; raw support indices are never
used in the quotient key.

For a finite world `W=(U,R,Phi)`, define

`C_Q(W) = (K_U(W), K_R(W))`,

where `K_U` is the sorted tuple of Unit quotient keys and `K_R` is the sorted
tuple of relation records whose endpoints have been replaced by the
corresponding quotient keys.

The auxiliary `Phi` payload is intentionally not folded into `C_Q`: Phi is the
separate map that must descend to the quotient.

## 3. Structural World Quotient Equivalence

Define

`W1 ~_W W2  <=>  C_Q(W1)=C_Q(W2)`.

Because the quotient keys are finite and unique, equality induces a unique
bijection

`f: U1 -> U2`

matching equal Unit quotient keys.

The relation part is preserved exactly when

`(i,j,type,evidence) in R1`

iff

`(f(i),f(j),type,evidence) in R2`.

Thus `~_W` is precisely the finite Unit-quotient graph isomorphism induced by
the frozen theta classes.

## 4. Structural World Quotient Theorem

### Theorem

Let `W1,W2` be finite theory-facing worlds generated from the frozen
observation-derived Unit construction. If

`W1 ~_W W2`,

then there exists a unique Unit bijection `f` such that

1. `u_i ~_U v_{f(i)}` for every Unit;
2. every explicit relation is transported by `f` with the same type and
   evidence;
3. no relation outside the supplied relation set is introduced.

### Proof

`W1 ~_W W2` means equality of `C_Q`. Therefore the two finite sets of Unit
quotient keys are equal. Strict theta injectivity on simple observations makes
each key identify at most one Unit in each generated family. Hence matching equal
keys defines a bijection `f`.

The equality of the relation component of `C_Q` states exactly that every
relation record in `W1` is mapped to an identical relation record in `W2`.
Conversely, every relation in `W2` is represented in the same finite relation
component, so the map is onto the relation set. Since relation formation is an
explicit candidate/predicate boundary, no additional relation can be inferred
by the quotient construction. QED.

## 5. Observation-relabelling commutativity

Let `pi` be a legal bijection of the observation index universe. Then

`T_{pi X}(pi A)=T_X(A)`.

Therefore every selected Unit keeps the same quotient key, while only its raw
support indices change. The relation endpoints are transported through the
induced Unit bijection. Consequently

`C_Q(W_X) = C_Q(W_{pi X})`.

Hence

`W_X ~_W W_{pi X}`.

This proves that the full chain

`X -> Gamma(X) -> P* -> U -> R -> W -> [W]`

commutes with legal observation relabeling, provided the Stage-2D selector and
relation evidence are themselves quotient-compatible.

## 6. Phi as a quotient-space map

A map `Phi: W -> R^23` is well-defined on the quotient space `W/~_W` iff

`W1 ~_W W2  =>  Phi(W1)=Phi(W2)`.

This condition is necessary and sufficient.

The previous implementation had an important boundary: `represent(world,
extractor)` deliberately accepted arbitrary raw-world extractors. Such an
extractor is **not automatically quotient-invariant**.

The frozen invariant path is now

`W -> C_Q(W) -> I(W) -> extractor -> R^23`.

`structural_invariant(W)` returns `C_Q(W)`, not the raw-index-dependent canonical
serialization. Therefore `represent_canonical` now receives only quotient data.

## 7. Phi audit result

There are two distinct statements:

### Safe theorem-level construction

If

`Phi_Q([W]) = F(C_Q(W))`,

for any explicitly supplied finite-valued extractor `F`, then Phi_Q is
well-defined on the quotient by construction: equivalent worlds have identical
`C_Q`, hence identical outputs.

### Raw-world extractor

For a function `F(W)` that directly reads Unit order or support indices,
well-definedness is **not automatic**. It must satisfy the finite audit condition

`W1 ~_W W2 => F(W1)=F(W2)`.

The implementation exposes `phi_well_defined_on_quotient` as a finite regression
certificate for this property.

## 8. What is proved and what is not

**Proved/frozen:**

- Unit quotient compatibility from observation-derived theta.
- Explicit Relation transport.
- Finite Structural World quotient equivalence.
- Existence and uniqueness of the induced Unit bijection on the simple finite
domain.
- Quotient-compatible structural invariant `I(W)=C_Q(W)`.
- Well-definedness of any representation constructed as `F(C_Q(W))`.

**Not silently proved:**

- Any particular numerical 23-D extractor is semantically complete.
- Any raw-world feature formula is quotient invariant merely because it has 23
  coordinates.
- Injectivity of `Phi` on World quotient classes.
- Equality of `Phi` with any external semantic notion.

## Verdict

The mathematical upstream chain is now closed through the World quotient:

`X -> Gamma(X) -> P* -> U -> R -> W -> [W]`.

The remaining requirement for v4.0 is no longer existence of a quotient. It is
the explicit selection and proof of the seven numerical coordinate formulas
for `Phi` and their semantic adequacy/information properties.
