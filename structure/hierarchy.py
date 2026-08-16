import numpy as np


class StructuralNode:
    """
    Generic structural hierarchy node

    Object
        |
        Part
            |
            Primitive

    """

    def __init__(
        self,
        node_type,
        data=None
    ):

        self.type=node_type

        self.data=data

        self.children=[]


    def add_child(
        self,
        node
    ):

        self.children.append(node)



    def print_tree(
        self,
        level=0
    ):

        indent="  "*level


        print(
            indent+
            self.type
        )


        if self.data is not None:

            print(
                indent,
                self.data
            )


        for c in self.children:

            c.print_tree(
                level+1
            )





class StructuralHierarchy:
    """
    Struct3D Hierarchical Representation


    Level:

    Object

        Part

            Primitive



    """



    def __init__(self):

        self.root=StructuralNode(
            "object"
        )



    # ==================================
    # Build hierarchy
    # ==================================

    def build(
        self,
        units
    ):


        for idx,u in enumerate(units):


            #
            # Part node
            #

            part=StructuralNode(

                "part"

            )


            #
            # Primitive node
            #

            primitive_data={

                "id":idx,

                "primitive":
                    u.primitive,


                "points":
                    len(u.points),


                "center":
                    np.mean(
                        u.points,
                        axis=0
                    ),


                "energy":
                    u.energy

            }



            primitive=StructuralNode(

                "primitive",

                primitive_data

            )



            part.add_child(
                primitive
            )


            self.root.add_child(
                part
            )



        return self



    # ==================================
    # Display
    # ==================================

    def show(self):

        print(
            "\nStructural Hierarchy"
        )


        self.root.print_tree()





    # ==================================
    # Query primitives
    # ==================================

    def primitives(self):


        result=[]


        for part in self.root.children:


            for primitive in part.children:


                result.append(
                    primitive.data
                )


        return result