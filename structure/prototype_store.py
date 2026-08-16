import os
import pickle


class PrototypeStore:
    """
    Struct3D Persistent Prototype Storage


    Prototype Memory
          |
          v
    Disk Storage


    save()
    load()

    """


    def __init__(
        self,
        path="data/prototype_memory.pkl"
    ):

        self.path = path



    # ==========================
    # Save
    # ==========================

    def save(
        self,
        prototypes
    ):


        folder=os.path.dirname(
            self.path
        )


        if folder and not os.path.exists(folder):

            os.makedirs(folder)



        with open(
            self.path,
            "wb"
        ) as f:


            pickle.dump(
                prototypes,
                f
            )



    # ==========================
    # Load
    # ==========================

    def load(
        self
    ):


        if not os.path.exists(
            self.path
        ):

            return []


        with open(
            self.path,
            "rb"
        ) as f:


            return pickle.load(
                f
            )



    # ==========================
    # Clear
    # ==========================

    def clear(
        self
    ):


        if os.path.exists(
            self.path
        ):

            os.remove(
                self.path
            )