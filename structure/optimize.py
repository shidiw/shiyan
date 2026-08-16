import numpy as np


class StructuralOptimizer:
    """
    Struct3D Variational Structural Optimizer


    Objective:

        E =
        PrimitiveFit
        +
        Boundary
        +
        Complexity


    """


    def __init__(
        self,
        merge_threshold=-0.01,
        split_threshold=0.3,
        boundary_weight=0.5
    ):

        self.merge_threshold = merge_threshold

        self.split_threshold = split_threshold

        self.boundary_weight = boundary_weight



    # =================================================
    # Main
    # =================================================

    def optimize(self, units):


        print("\nOptimization")


        before=self.total_energy(units)


        print(
            "Before:",
            before
        )


        units=self.merge_pass(
            units
        )


        units=self.split_pass(
            units
        )


        after=self.total_energy(units)


        print(
            "After:",
            after
        )


        # 防止能量增加

        if after > before:

            print(
                "Reject optimization"
            )

            return units


        return units




    # =================================================
    # Merge
    # =================================================


    def merge_pass(self,units):


        changed=True


        while changed:


            changed=False

            best=None

            best_cost=0



            for i in range(len(units)):

                for j in range(i+1,len(units)):


                    c=self.merge_cost(
                        units[i],
                        units[j]
                    )


                    if c < best_cost:


                        best_cost=c

                        best=(i,j)



            if best is not None:


                i,j=best


                print(
                    "Optimizer merge:",
                    i,
                    j,
                    best_cost
                )


                units=self.combine(
                    units,
                    i,
                    j
                )


                changed=True



        return units





    # =================================================
    # Merge Cost
    # =================================================


    def merge_cost(self,a,b):


        from structure.primitive_selector import PrimitiveSelector
        from structure.unit import StructuralUnit


        selector=PrimitiveSelector()


        Ea=selector.predict(a)["energy"]

        Eb=selector.predict(b)["energy"]



        pts=np.concatenate(
            [
                a.points,
                b.points
            ],
            axis=0
        )


        merged=StructuralUnit(
            pts,
            "unknown"
        )


        Em=selector.predict(
            merged
        )["energy"]



        return Em-Ea-Eb





    # =================================================
    # Combine
    # =================================================


    def combine(
        self,
        units,
        i,
        j
    ):


        from structure.unit import StructuralUnit


        pts=np.concatenate(
            [
                units[i].points,
                units[j].points
            ],
            axis=0
        )


        new=StructuralUnit(
            pts,
            "unknown"
        )


        result=[]


        for k,u in enumerate(units):

            if k!=i and k!=j:

                result.append(u)


        result.append(new)


        return result





    # =================================================
    # Split
    # =================================================


    def split_pass(self,units):


        result=[]


        for u in units:


            e=self.unit_energy(u)


            if e > self.split_threshold:


                print(
                    "Split candidate energy:",
                    e
                )


                children=self.split_unit(u)


                result.extend(children)


            else:

                result.append(u)



        return result





    def split_unit(self,u):


        pts=u.points


        center=np.mean(
            pts,
            axis=0
        )


        X=pts-center


        _,_,V=np.linalg.svd(X)


        axis=V[0]


        proj=X@axis


        mask=proj>0



        from structure.unit import StructuralUnit


        return [

            StructuralUnit(
                pts[mask],
                "unknown"
            ),

            StructuralUnit(
                pts[~mask],
                "unknown"
            )

        ]






    # =================================================
    # Energy
    # =================================================


    def total_energy(self,units):


        e=0


        for u in units:

            e+=self.unit_energy(u)



        e+=self.boundary_energy(
            units
        )


        return e





    def unit_energy(self,u):


        from structure.primitive_selector import PrimitiveSelector


        selector=PrimitiveSelector()


        result=selector.predict(u)


        return result["energy"]






    # =================================================
    # Boundary
    # =================================================


    def boundary_energy(self,units):


        e=0


        for i in range(len(units)):

            for j in range(i+1,len(units)):


                ci=np.mean(
                    units[i].points,
                    axis=0
                )


                cj=np.mean(
                    units[j].points,
                    axis=0
                )


                d=np.linalg.norm(
                    ci-cj
                )


                e+=1/(d+1e-6)



        return self.boundary_weight*e