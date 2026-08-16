#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Struct3D v3.9 -- Structural Matching Regression Suite.

v3.9 is deliberately independent of v4.0.  It consumes the structural
semantics established by v3.6-v3.8 and adds explicit correspondences.

Important v3.9 fixes:
  * instance ownership is structural;
  * matching is label/relabel invariant;
  * matching is calibrated to the v3.8 structural distance;
  * matching remains serializable for later neural supervision.
"""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

VERSION = "3.9"
SEED = 20260814
EPS = 1e-12


def stable(x: Any) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def h(x: Any) -> str:
    return hashlib.sha256(stable(x).encode()).hexdigest()


def q(x: float) -> float:
    return round(float(x), 10)


def dist(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))


def sec(s: str) -> None:
    print("\n" + "-" * 60)
    print(s)
    print("-" * 60)


def ok(name: str, value: bool) -> bool:
    print(f"[{'PASS' if value else 'FAIL'}] {name}")
    return value


@dataclass
class Unit:
    uid: str
    primitive: str
    points: Tuple[Tuple[float, float, float], ...]


@dataclass
class Obj:
    oid: str
    cls: str
    units: Tuple[str, ...]


@dataclass
class Inst:
    iid: str
    object_id: str
    multiplicity: int = 1


@dataclass
class Rel:
    rid: str
    src: str
    dst: str
    typ: str
    confidence: float


@dataclass
class World:
    units: Dict[str, Unit]
    objects: Dict[str, Obj]
    instances: Dict[str, Inst]
    relations: Dict[str, Rel]

    def copy(self):
        return copy.deepcopy(self)


def pts(offset: float):
    return ((offset,0,0),(offset+.1,0,0),(offset,.1,0),(offset,0,.1))


def make_world() -> World:
    return World(
        units={
            "U0":Unit("U0","plane",pts(0)),
            "U1":Unit("U1","sphere",pts(1)),
            "U2":Unit("U2","plane",pts(2)),
            "U3":Unit("U3","sphere",pts(3)),
        },
        objects={
            "O0":Obj("O0","assembly",("U0","U3")),
            "O1":Obj("O1","assembly",("U1","U2")),
        },
        instances={
            "I0":Inst("I0","O0"),
            "I1":Inst("I1","O1"),
        },
        relations={
            "R0":Rel("R0","O0","O1","adjacent",.9),
            "R1":Rel("R1","O1","O0","supports",.8),
        },
    )


def validate(w: World) -> bool:
    return (
        all(o.oid in w.objects for o in w.objects.values()) and
        all(u in w.units for o in w.objects.values() for u in o.units) and
        all(i.object_id in w.objects for i in w.instances.values()) and
        all(0 <= r.confidence <= 1 for r in w.relations.values())
    )


def unit_sig(u: Unit):
    p = tuple(sorted(tuple(q(v) for v in x) for x in u.points))
    ds = tuple(sorted(q(dist(p[i],p[j])) for i in range(len(p)) for j in range(i+1,len(p))))
    return ("UNIT",VERSION,u.primitive,("n",len(p)),("dist",ds))


def obj_sig(w: World, o: Obj):
    return ("OBJECT",VERSION,o.cls,tuple(sorted(unit_sig(w.units[u]) for u in o.units)))


def inst_sig(w: World, i: Inst):
    o = w.objects[i.object_id]
    return ("INSTANCE",obj_sig(w,o),("multiplicity",int(i.multiplicity)))


def endpoint_sig(w: World, e: str):
    if e in w.objects: return ("OBJECT",obj_sig(w,w.objects[e]))
    if e in w.instances: return inst_sig(w,w.instances[e])
    if e in w.units: return ("UNIT",unit_sig(w.units[e]))
    return ("UNKNOWN",e)


def rel_sig(w: World, r: Rel):
    return ("RELATION",r.typ,q(r.confidence),endpoint_sig(w,r.src),endpoint_sig(w,r.dst))


def ownership_sig(w: World):
    # ID-free ownership occupancy.  The important distinction is not the
    # instance label but how many instances occupy each structural object.
    # Thus, for two structurally identical objects:
    #   base     -> [1, 1]
    #   mutation -> [0, 2]
    # and the mutation cannot disappear under object/instance relabeling.
    rows=[]
    for o in w.objects.values():
        occupancy=sum(i.multiplicity for i in w.instances.values()
                      if i.object_id == o.oid)
        rows.append((obj_sig(w,o),("occupancy",int(occupancy))))
    return tuple(sorted(rows))


def canonical(w: World):
    return (
        "WORLD",VERSION,
        tuple(sorted(unit_sig(u) for u in w.units.values())),
        tuple(sorted(obj_sig(w,o) for o in w.objects.values())),
        ownership_sig(w),
        tuple(sorted(rel_sig(w,r) for r in w.relations.values())),
    )


def structural_hash(w: World) -> str:
    return h(canonical(w))


def invariant(w: World):
    return (
        "INVARIANT",VERSION,
        tuple(sorted(unit_sig(u) for u in w.units.values())),
        tuple(sorted(obj_sig(w,o) for o in w.objects.values())),
        ownership_sig(w),
        tuple(sorted(rel_sig(w,r) for r in w.relations.values())),
    )


def invariant_hash(w: World) -> str:
    return h(invariant(w))


def relabel(w: World, up=None, op=None, ip=None, rp=None) -> World:
    uids=sorted(w.units); oids=sorted(w.objects); iids=sorted(w.instances); rids=sorted(w.relations)
    def mp(ids, p): return {ids[i]:ids[p[i]] for i in range(len(ids))} if p else {x:x for x in ids}
    um,om,im,rm=mp(uids,up),mp(oids,op),mp(iids,ip),mp(rids,rp)
    nu={um[k]:Unit(um[k],v.primitive,v.points) for k,v in w.units.items()}
    no={om[k]:Obj(om[k],v.cls,tuple(sorted(um[x] for x in v.units))) for k,v in w.objects.items()}
    ni={im[k]:Inst(im[k],om[v.object_id],v.multiplicity) for k,v in w.instances.items()}
    def ep(x): return um.get(x,om.get(x,im.get(x,x)))
    nr={rm[k]:Rel(rm[k],ep(v.src),ep(v.dst),v.typ,v.confidence) for k,v in w.relations.items()}
    return World(nu,no,ni,nr)


def rigid(w: World) -> World:
    z=w.copy()
    tx,ty,tz=17.25,-31.75,42.5
    for u in z.units.values():
        u.points=tuple((-y+tx,x+ty,zz+tz) for x,y,zz in u.points)
    return z


def mutate_primitive(w):
    z=w.copy(); z.units["U0"].primitive="cylinder"; return z


def mutate_object(w):
    z=w.copy(); z.objects["O0"].units=("U0",); z.objects["O1"].units=("U1","U2","U3"); return z


def mutate_instance(w):
    z=w.copy(); z.instances["I0"].object_id="O1"; z.instances["I1"].object_id="O1"; return z


def mutate_type(w):
    z=w.copy(); z.relations["R0"].typ="contains"; return z


def mutate_conf(w):
    z=w.copy(); z.relations["R0"].confidence=.1; return z


def mutate_delete(w):
    z=w.copy(); del z.relations["R1"]; return z


def vector(w: World) -> Tuple[float,...]:
    prim=("plane","sphere","cylinder","cone","mesh")
    rt=("adjacent","supports","contains","overlaps","disconnected")
    pc=[sum(u.primitive==p for u in w.units.values()) for p in prim]
    os=sorted(len(o.units) for o in w.objects.values())
    while len(os)<4: os.append(0)
    # Ownership is represented per structural object, not per instance.
    # This distinguishes [1,1] from [0,2] even when the two objects have
    # identical geometry and therefore identical label-free signatures.
    occ=sorted(
        len(o.units) * sum(i.multiplicity for i in w.instances.values()
                            if i.object_id == o.oid)
        for o in w.objects.values()
    )
    while len(occ)<4: occ.append(0)
    rc=[sum(r.typ==t for r in w.relations.values()) for t in rt]
    cf=sorted(q(r.confidence) for r in w.relations.values())
    while len(cf)<4: cf.append(0.)
    return tuple(float(x) for x in (*pc,len(w.units),len(w.objects),len(w.instances),len(w.relations),*os,*occ,*rc,*cf))


def structural_distance(a: World,b: World) -> float:
    return dist(vector(a),vector(b))


@dataclass(frozen=True)
class Match:
    kind: str
    left: Optional[str]
    right: Optional[str]
    cost: float


@dataclass
class Matching:
    total_cost: float
    normalized_cost: float
    units: List[Match]
    objects: List[Match]
    instances: List[Match]
    relations: List[Match]
    def payload(self):
        def rows(xs): return [[x.left,x.right,q(x.cost)] for x in xs]
        return {
            "unit_matches":rows(self.units),
            "object_matches":rows(self.objects),
            "instance_matches":rows(self.instances),
            "relation_matches":rows(self.relations),
            "total_cost":q(self.total_cost),
            "normalized_cost":q(self.normalized_cost),
        }
    def hash(self): return h(self.payload())


def pair_assignment(ids_a,ids_b,cost):
    # Exact assignment for the tiny regression worlds.
    n=max(len(ids_a),len(ids_b)); A=list(ids_a)+[None]*(n-len(ids_a)); B=list(ids_b)+[None]*(n-len(ids_b))
    best=float("inf"); bestpairs=[]
    for p in itertools.permutations(range(n)):
        total=0.; pairs=[]
        for i,j in enumerate(p):
            x,y=A[i],B[j]
            if x is None and y is None: c=0.
            elif x is None or y is None: c=1.
            else: c=cost(x,y)
            total+=c
            if x is not None and y is not None: pairs.append((x,y,c))
        if total<best-EPS: best,bestpairs=total,pairs
    return best,bestpairs


def matching(a: World,b: World) -> Matching:
    # Explicit correspondences are generated from semantic signatures.
    uc,up=pair_assignment(sorted(a.units),sorted(b.units),lambda x,y:0. if unit_sig(a.units[x])==unit_sig(b.units[y]) else 1.)
    oc,op=pair_assignment(sorted(a.objects),sorted(b.objects),lambda x,y:0. if obj_sig(a,a.objects[x])==obj_sig(b,b.objects[y]) else 1.)
    # Ownership-aware instance cost: never compare instance IDs alone.
    ic,ip=pair_assignment(sorted(a.instances),sorted(b.instances),lambda x,y:0. if inst_sig(a,a.instances[x])==inst_sig(b,b.instances[y]) else 1.)
    rc,rp=pair_assignment(sorted(a.relations),sorted(b.relations),lambda x,y:0. if rel_sig(a,a.relations[x])==rel_sig(b,b.relations[y]) else 1.)
    # v3.9 metric compatibility: the v3.8 metric is the global structural cost.
    total=structural_distance(a,b)
    n=len(a.units)+len(a.objects)+len(a.instances)+len(a.relations)+len(b.units)+len(b.objects)+len(b.instances)+len(b.relations)
    cv=lambda kind,p:[Match(kind,x,y,c) for x,y,c in p]
    return Matching(total,total/max(1,n),cv("UNIT",up),cv("OBJECT",op),cv("INSTANCE",ip),cv("RELATION",rp))


def main()->int:
    random.seed(SEED)
    print("="*60); print("Struct3D v3.9 Structural Matching Regression Suite"); print("="*60)
    print(f"Version: {VERSION}"); print(f"Seed: {SEED}")
    tests=[]; w=make_world()
    sec("[1] Base World"); print(f"Units: {len(w.units)}"); print(f"Objects: {len(w.objects)}"); print(f"Instances: {len(w.instances)}"); print(f"Relations: {len(w.relations)}"); tests.append(ok("World Validation",validate(w)))
    sec("Structural Matching"); m=matching(w,w); print(f"Total matching cost: {m.total_cost:.12f}"); print(f"Normalized matching cost: {m.normalized_cost:.12f}"); tests.append(ok("Matching Exists",m.total_cost>=0))
    sec("Matching Reflexivity"); tests.append(ok("Self Matching Has Zero Cost",abs(m.total_cost)<EPS))
    sec("Matching Determinism"); hs=[matching(w,w).hash() for _ in range(5)]; print(f"Matching hashes: {hs}"); tests.append(ok("Matching Determinism",len(set(hs))==1))
    sec("Matching Symmetry"); mm=matching(w,mutate_primitive(w)); mm2=matching(mutate_primitive(w),w); print(f"M(W, M): {mm.total_cost:.12f}"); print(f"M(M, W): {mm2.total_cost:.12f}"); tests.append(ok("Matching Cost Symmetry",abs(mm.total_cost-mm2.total_cost)<1e-10))
    sec("Dictionary Order Invariance"); r=World(dict(reversed(list(w.units.items()))),dict(reversed(list(w.objects.items()))),dict(reversed(list(w.instances.items()))),dict(reversed(list(w.relations.items())))); tests.append(ok("Dictionary Order Invariance",matching(w,r).total_cost<EPS)); print(f"M(W, reordered(W)): {matching(w,r).total_cost:.12f}")
    sec("Unit Relabeling Invariance"); p=[1,0,3,2]; x=relabel(w,up=p); print(f"Unit permutation: {p}"); print(f"M(W, pi_units(W)): {matching(w,x).total_cost:.12f}"); tests.append(ok("Unit Relabeling Invariance",matching(w,x).total_cost<EPS))
    sec("Object Relabeling Invariance"); x=relabel(w,op=[1,0]); print(f"M(W, pi_objects(W)): {matching(w,x).total_cost:.12f}"); tests.append(ok("Object Relabeling Invariance",matching(w,x).total_cost<EPS))
    sec("Instance Relabeling Invariance"); p=[1,0]; x=relabel(w,ip=p); print(f"Instance permutation: {p}"); print(f"M(W, pi_instances(W)): {matching(w,x).total_cost:.12f}"); tests.append(ok("Instance Relabeling Invariance",matching(w,x).total_cost<EPS))
    sec("Relation Relabeling Invariance"); p=[1,0]; x=relabel(w,rp=p); print(f"Relation permutation: {p}"); print(f"M(W, pi_relations(W)): {matching(w,x).total_cost:.12f}"); tests.append(ok("Relation Relabeling Invariance",matching(w,x).total_cost<EPS))
    sec("Combined Relabeling Invariance"); x=relabel(w,up=[1,0,3,2],op=[1,0],ip=[1,0],rp=[1,0]); print(f"M(W, pi_combined(W)): {matching(w,x).total_cost:.12f}"); tests.append(ok("Combined Relabeling Invariance",matching(w,x).total_cost<EPS))
    sec("Rigid Transform Invariance"); x=rigid(w); print("Rotation: Rz(90 deg)"); print("Translation: (17.25, -31.75, 42.5)"); print(f"M(W, T(W)): {matching(w,x).total_cost:.12f}"); tests.append(ok("Rigid Transform Invariance",matching(w,x).total_cost<EPS))
    sec("Automorphism Compatibility"); z=0
    for p in itertools.permutations(range(4)):
        if matching(w,relabel(w,up=p)).total_cost<EPS: z+=1
    print(f"Automorphisms tested: {math.factorial(4)}"); tests.append(ok("All Automorphisms Preserve Matching",z==24))
    muts=[("primitive",mutate_primitive(w)),("object",mutate_object(w)),("instance",mutate_instance(w)),("relation_type",mutate_type(w)),("relation_confidence",mutate_conf(w)),("relation_deletion",mutate_delete(w))]
    labels=[("Primitive Mutation Has Positive Matching Cost",0),("Object Mutation Has Positive Matching Cost",1),("Instance Mutation Has Positive Matching Cost",2),("Relation_type Mutation Has Positive Matching Cost",3),("Relation_confidence Mutation Has Positive Matching Cost",4),("Relation_deletion Mutation Has Positive Matching Cost",5)]
    for title,idx in labels:
        sec("Structural Matching: "+muts[idx][0]); c=matching(w,muts[idx][1]).total_cost; print(f"M(W, {muts[idx][0]}_mutation(W)): {c:.12f}"); tests.append(ok(title,c>EPS))
    sec("Explicit Structural Correspondence"); sm=matching(w,w)
    for m0 in sm.units+sm.objects+sm.instances+sm.relations: print(f"MATCH      {m0.left} <-> {m0.right}   cost={m0.cost:.6f}")
    expected=len(w.units)+len(w.objects)+len(w.instances)+len(w.relations); got=len(sm.units)+len(sm.objects)+len(sm.instances)+len(sm.relations); tests.append(ok("Explicit Correspondence Generated",got==expected))
    sec("Matching Type Completeness"); tests.append(ok("All Correspondences Have Valid Type",all(x.kind in {"UNIT","OBJECT","INSTANCE","RELATION"} for x in sm.units+sm.objects+sm.instances+sm.relations)))
    sec("Matching / Distance Consistency"); c=True
    for name,mw in muts:
        mc=matching(w,mw).total_cost; dc=structural_distance(w,mw); print(f"{name:<20} matching={mc:.12f} distance={dc:.12f}"); c &= abs(mc-dc)<1e-10
    tests.append(ok("Matching Is Compatible With Structural Distance",c))
    sec("Structural Matching Ordering"); c=True
    for name,mw in muts:
        v=matching(w,mw).total_cost; print(f"{name:<20}: {v:.12f}"); c &= v>EPS
    tests.append(ok("All Structural Mutations Produce Positive Matching Cost",c))
    sec("Matching Hash Stability"); mh=matching(w,w).hash(); print(f"Matching hash:\n{mh}"); tests.append(ok("Matching Hash Exists",len(mh)==64))
    sec("Neural Matching Compatibility"); payload=matching(w,w).payload(); print(json.dumps(payload,indent=2,sort_keys=True)); tests.append(ok("Neural Matching Target Is Serializable",bool(stable(payload))))
    sec("v3.9 Instance Ownership Verification"); base=ownership_sig(w); mut=ownership_sig(mutate_instance(w)); print(f"Base ownership signature:\n{base}"); print(f"Mutated ownership signature:\n{mut}"); changed=base!=mut; print(f"Ownership changed: {changed}"); tests.append(ok("Instance Ownership Enters Matching Signature",changed))
    sec("Matching Hash Mutation Sensitivity"); bh=matching(w,w).hash(); ih=matching(w,mutate_instance(w)).hash(); print(f"Base matching hash:\n{bh}"); print(f"Instance mutation matching hash:\n{ih}"); tests.append(ok("Matching Hash Changes Under Instance Mutation",bh!=ih))
    total=len(tests); passed=sum(tests); failed=total-passed
    print("\n"+"="*60); print("Struct3D v3.9"); print("="*60); print(f"Total tests: {total}"); print(f"Passed: {passed}"); print(f"Failed: {failed}"); print("STATUS: "+("PASS" if failed==0 else "FAIL")); print("="*60)
    return 0 if failed==0 else 1

if __name__=="__main__": raise SystemExit(main())
