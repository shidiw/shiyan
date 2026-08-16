import numpy as np

from structure.unit import StructuralUnit
from structure.primitive_selector import PrimitiveSelector




class StructuralMerger:
    """
    Struct3D Structural Merge v0.2


    Objective:


        min

        E(A∪B)

        -

        E(A)

        -

        E(B)

        +

        λR(A,B)



    where:

        R = structural incompatibility


    """



    def __init__(
        self,
        threshold=0.02
    ):


        self.threshold = threshold


        self.selector = PrimitiveSelector()



        self.lambda_structure = 0.5





    # ==================================================
    # Main
    # ==================================================

    def merge(
        self,
        units
    ):


        units=list(units)



        changed=True



        while changed:


            changed=False


            best_pair=None

            best_cost=np.inf



            n=len(units)



            for i in range(n):


                for j in range(i+1,n):



                    cost=self.merge_cost(

                        units[i],

                        units[j]

                    )



                    if cost < best_cost:


                        best_cost=cost

                        best_pair=(i,j)




            if (

                best_pair is not None

                and

                best_cost < 0

            ):


                i,j=best_pair



                print(

                    "\nMerge:",

                    i,

                    j,

                    "cost:",

                    best_cost

                )



                new_unit=self.combine(

                    units[i],

                    units[j]

                )



                units.pop(j)

                units.pop(i)


                units.append(
                    new_unit
                )



                changed=True





        return units





    # ==================================================
    # Merge Cost
    # ==================================================

    def merge_cost(
        self,
        a,
        b
    ):



        Ea=self.unit_energy(a)

        Eb=self.unit_energy(b)



        merged=self.combine(
            a,
            b
        )



        result=self.selector.predict(
            merged
        )


        Eab=result["energy"]



        penalty=self.structure_penalty(
            a,
            b
        )



        return (

            Eab

            -

            Ea

            -

            Eb

            +

            self.lambda_structure*

            penalty

        )





    # ==================================================
    # Structure Penalty
    # ==================================================

    def structure_penalty(
        self,
        a,
        b
    ):


        pa=getattr(
            a,
            "primitive",
            "unknown"
        )


        pb=getattr(
            b,
            "primitive",
            "unknown"
        )


        if pa=="merged" or pb=="merged":

            return 1.0



        if pa==pb:

            return 0.0



        return 10.0





    # ==================================================
    # Unit Energy
    # ==================================================

    def unit_energy(
        self,
        unit
    ):



        if (

            hasattr(unit,"energy")

            and

            unit.energy is not None

        ):


            return unit.energy




        result=self.selector.predict(
            unit
        )


        unit.primitive=result["primitive"]

        unit.energy=result["energy"]



        return result["energy"]





    # ==================================================
    # Combine
    # ==================================================

    def combine(
        self,
        a,
        b
    ):


        points=np.concatenate(
            [
                a.points,
                b.points
            ],
            axis=0
        )


        unit=StructuralUnit(
            points,
            primitive="merged"
        )


        return unit