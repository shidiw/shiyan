# Struct3D observation-derived Unit parameter closure

## Definition

Let

\[
X=(x_i)_{i\in\Omega_X},\qquad x_i\in\mathbb R^3,
\]

be a finite **simple observation**, meaning \(x_i\neq x_j\) for \(i\neq j\),
and let \(A\subseteq\Omega_X\), \(A\neq\varnothing\). Define

\[
T_X(A)=\theta_A
\]

by the finite signature

\[
\theta_A=\Bigl(|A|,\bar x_A,S_X(A)\Bigr),
\]

where

\[
\bar x_A=\frac1{|A|}\sum_{i\in A}x_i,
\qquad
S_X(A)=\operatorname{sort}_{lex}\{x_i:i\in A\}.
\]

The complete sorted coordinate signature is retained. The centroid is a
redundant but interpretable geometric summary.

The observation-derived Unit is

\[
U_X(A)=\bigl(A,T_X(A)\bigr).
\]

No semantic label, primitive class, learned representation, threshold,
optimization rule, or neural network occurs in the definition.

## Proposition 1 — Finiteness

For finite \(X\) and non-empty finite \(A\), \(T_X(A)\) is a finite tuple of
finite real values.

## Proposition 2 — Strict injectivity on geometric blocks

For a simple observation, if

\[
T_X(A)=T_X(B),
\]

then

\[
S_X(A)=S_X(B).
\]

Because all observed coordinates are distinct, equality of the sorted coordinate
sets implies \(A=B\). Therefore \(T_X\) is strictly injective on the finite
block family \(\Pi(\Omega_X)\).

This is the exact reason the simplicity assumption is part of the frozen
mathematical domain. Without it, two different indices carrying exactly the
same coordinate cannot be distinguished by any relabeling-invariant geometric
parameter map.

## Proposition 3 — Relabeling / quotient compatibility

Let \(\pi:\Omega_X\to\Omega_X\) be a bijection and define the relabeled
observation \(\pi X\) by

\[
(\pi X)_{\pi(i)}=x_i.
\]

Then

\[
T_{\pi X}(\pi A)=T_X(A).
\]

Relabeling changes only indices, while the coordinate set in the block is
unchanged. Hence

\[
U_{\pi X}(\pi A)=\bigl(\pi A,T_X(A)\bigr)=\pi U_X(A).
\]

Thus \(U_X\) descends to the observation relabeling quotient.

## Theorem — Observation-derived Unit Formation

Let

\[
P^*\in\arg\min_{P\in\Gamma(X)}E_{2D}(P),
\]

where \(\Gamma(X)=A_{max}(X)\) is the frozen finite, non-empty,
quotient-compatible admissible family. For every block \(A\in P^*\), define

\[
U_A=U_X(A)=\bigl(A,T_X(A)\bigr).
\]

Then the selected partition induces the finite Structural Unit family

\[
U(P^*,X)=\{U_X(A):A\in P^*\}.
\]

Under every legal relabeling \(\pi\),

\[
U(\pi P^*,\pi X)=\pi U(P^*,X).
\]

Therefore the map

\[
X\longrightarrow\Gamma(X)
\longrightarrow P^*
\longrightarrow U(P^*,X)
\]

is closed at the Unit-formation level without semantic labels or learned
representations.

## Relation to Stage 2D Energy

Stage 2D is the selector, not the definition of \(\theta\):

\[
X
\xrightarrow{\Gamma=A_{max}}
\Gamma(X)
\xrightarrow{\arg\min E_{2D}}
P^*
\xrightarrow{T_X}
U(P^*,X).
\]

The Stage 2D unit term and boundary term determine which partition is selected;
\(T_X\) deterministically attaches the observation-derived geometric parameter
to every selected Unit. Thus changing the energy changes \(P^*\), but does not
silently redefine the Unit parameter map.

## Scope boundary

Strict injectivity is with respect to the fixed observed coordinate frame and
the simple-observation domain. This theorem does not claim invariance to
arbitrary Euclidean transformations. Such invariance would require an explicit
geometric quotient and a different parameter map.
