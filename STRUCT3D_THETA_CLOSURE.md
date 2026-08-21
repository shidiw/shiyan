# Struct3D observation-derived Unit parameter closure

## Definition

Let

\[
X=(x_i)_{i\in\Omega_X},\qquad x_i\in\mathbb R^3,
\]

be a finite observation and let \(A\subseteq\Omega_X\), \(A\neq\varnothing\).
Define

\[
T_X(A)=\theta_A
\]

by the finite signature

\[
\theta_A=
\Bigl(|A|,\bar x_A,S_X(A)\Bigr),
\]

where

\[
\bar x_A=\frac1{|A|}\sum_{i\in A}x_i
\]

and

\[
S_X(A)=\operatorname{sort}_{lex}\{x_i:i\in A\}.
\]

The complete sorted coordinate signature is deliberately retained. The centroid
is redundant for injectivity but provides a directly interpretable geometric
summary.

The observation-derived Unit is therefore

\[
U_X(A)=\bigl(A,T_X(A)\bigr).
\]

No semantic label, primitive class, learned representation, threshold, or
neural network occurs in the definition.

## Proposition 1 — Finiteness

For finite \(X\) and non-empty finite \(A\), \(T_X(A)\) is a finite tuple of
finite real values.

## Proposition 2 — Strict injectivity on geometric blocks

For a fixed observation coordinate frame, if

\[
T_X(A)=T_X(B),
\]

then

\[
\{x_i:i\in A\}=\{x_i:i\in B\}
\]

as coordinate multisets. Since the observation indices are distinct points in
the frozen candidate construction, distinct geometric blocks have distinct
signatures. Thus \(T_X\) is strictly injective on the finite geometric block
family.

The proof is immediate from equality of the complete sorted coordinate
signature \(S_X(A)=S_X(B)\).

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

The proof follows because relabeling changes only indices; the coordinate
multiset \(\{x_i:i\in A\}\) is unchanged.

Consequently

\[
U_{\pi X}(\pi A)
=\bigl(\pi A,T_X(A)\bigr),
\]

which is exactly the Unit quotient action induced by the observation
relabeling.

## Theorem — Observation-derived Unit Formation

Let

\[
P^*=\arg\min_{P\in\Gamma(X)}E_{2D}(P),
\]

where \(\Gamma(X)=A_{max}(X)\) is the frozen finite, non-empty,
quotient-compatible admissible family. For every block \(A\in P^*\), define

\[
U_A=U_X(A)=\bigl(A,T_X(A)\bigr).
\]

Then the selected partition induces a finite Structural Unit family

\[
U(P^*,X)=\{U_X(A):A\in P^*\}
\]

without importing semantic information or a learned representation.

Moreover, under any legal observation relabeling \(\pi\),

\[
U(\pi P^*,\pi X)=\pi U(P^*,X),
\]

so Unit formation descends to the observation quotient.

## Relation to Stage 2D Energy

Stage 2D remains the selector, not the definition of \(\theta\):

\[
X\longrightarrow\Gamma(X)
\xrightarrow{\arg\min E_{2D}}P^*
\longrightarrow
\{(A,T_X(A)):A\in P^*\}.
\]

The unit term and boundary term determine which partition is selected, while
\(T_X\) determines the semantic-free geometric parameter attached to each
selected Unit. This separation is essential: changing the energy changes
\(P^*\), but does not silently redefine the Unit parameter map.

## Scope boundary

Strict injectivity is with respect to the observed geometric coordinate frame.
This theorem does not claim invariance to arbitrary Euclidean transformations;
those would require an explicitly chosen geometric quotient and a different
parameter map.
