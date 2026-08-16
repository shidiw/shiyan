import numpy as np
from collections import deque

from .unit import StructuralUnit



class GraphStructuralCluster:
    """
    Graph based Structural Unit Extraction


    Input:

        Structural Graph

            G=(V,E,W)


    Output:

        Structural Units


    """


    def __init__(
        self,
        threshold=0.5,
        min_points=50
    ):


        self.threshold = threshold

        self.min_points = min_points



    # =====================================
    # Main API
    # =====================================


    def extract(
        self,
        points,
        graph
    ):
        """
        Extract connected structural regions

        """


        edges = graph["edges"]

        weights = graph["weights"]



        N=len(points)



        adjacency=[

            []

            for _ in range(N)

        ]



        # build high affinity graph

        for e,w in zip(
            edges,
            weights
        ):


            if w >= self.threshold:


                i,j=e


                adjacency[i].append(j)

                adjacency[j].append(i)



        components = (

            self.connected_components(

                adjacency

            )

        )



        units=[]



        for cid,indices in enumerate(
            components
        ):



            if len(indices)<self.min_points:

                continue



            pts=points[indices]



            unit=StructuralUnit(

                pts,

                primitive="unknown",

                indices=np.array(indices)

            )


            units.append(
                unit
            )



        return units



    # =====================================
    # Connected Components
    # =====================================


    def connected_components(
        self,
        adjacency
    ):


        N=len(adjacency)


        visited=np.zeros(
            N,
            dtype=bool
        )


        components=[]



        for i in range(N):


            if visited[i]:

                continue



            queue=deque([i])


            visited[i]=True


            component=[]



            while queue:


                v=queue.popleft()


                component.append(v)



                for n in adjacency[v]:


                    if not visited[n]:


                        visited[n]=True

                        queue.append(n)



            components.append(
                component
            )



        return components



    # =====================================
    # Statistics
    # =====================================


    def statistics(
        self,
        units
    ):


        print(
            "\nGraph Structural Units"
        )


        print(
            "Number:",
            len(units)
        )



        for i,u in enumerate(units):


            print(

                "Unit",

                i,

                "points:",

                u.size()

            )