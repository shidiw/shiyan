import numpy as np


class StructuralEmbedding:
    """
    Structural Embedding v2.0


    Object
       |
       |
       v

    invariant structural vector


    Removed:
        absolute center


    Added:
        primitive invariant
        geometry parameters
        energy descriptor


    """



    def __init__(
        self,
        dimension=64
    ):

        self.dimension = dimension




    # =====================================================
    # Primitive Encoding
    # =====================================================

    def encode_primitive(
        self,
        primitive
    ):

        """
        primitive type embedding


        plane
        sphere
        cylinder


        """

        if isinstance(
            primitive,
            list
        ):
            primitive = primitive[0]



        vector=np.zeros(8)



        if primitive=="plane":

            vector[0]=1.0


        elif primitive=="sphere":

            vector[1]=1.0


        elif primitive=="cylinder":

            vector[2]=1.0


        else:

            vector[3]=1.0



        return vector





    def encode_parameters(
        self,
        parameters
    ):

        """
        Encode structural shape parameters.

        Supported input:

            dict
            list[dict]

        Position-related parameters such as
        'center' are excluded because absolute
        position must not define structural identity.
        """

        vec = np.zeros(16, dtype=float)

        if parameters is None:
            return vec

        # --------------------------------------------------
        # Canonicalize
        # --------------------------------------------------

        if isinstance(parameters, dict):

            parameter_dicts = [
                parameters
            ]

        elif isinstance(parameters, (list, tuple)):

            parameter_dicts = [
                p for p in parameters
                if isinstance(p, dict)
            ]

        else:

            return vec

        # --------------------------------------------------
        # Encode each structural parameter set
        # --------------------------------------------------

        index = 0

        for param_dict in parameter_dicts:

            for k, v in param_dict.items():

                # ------------------------------------------
                # Absolute position is not structural
                # ------------------------------------------

                if k in [
                    "center",
                ]:

                    continue

                if index >= 16:

                    break

                # ------------------------------------------
                # Numeric conversion
                # ------------------------------------------

                arr = np.asarray(
                    v,
                    dtype=float
                )

                if arr.ndim == 0:

                    vec[index] = float(arr)

                    index += 1

                else:

                    flat = arr.reshape(-1)

                    remaining = 16 - index

                    count = min(
                        len(flat),
                        remaining
                    )

                    vec[
                        index:index + count
                    ] = flat[:count]

                    index += count

            if index >= 16:

                break

        return vec






    # =====================================================
    # Geometry Normalization
    # =====================================================

    def normalize_vector(
        self,
        x
    ):


        norm=np.linalg.norm(
            x
        )


        if norm<1e-8:

            return x


        return x/norm





    # =====================================================
    # Object Encoding
    # =====================================================

    def encode_object(
        self,
        obj
    ):


        primitive_feature = self.encode_primitive(

            obj.get(
                "primitive",
                None
            )

        )



        parameter_feature = self.encode_parameters(

            obj.get(
                "parameters",
                None
            )

        )



        energy_feature=np.zeros(8)



        if "energy" in obj:


            e=float(
                obj["energy"]
            )


            energy_feature[0]=e



        # concatenate


        feature=np.concatenate(

            [

                primitive_feature,

                parameter_feature,

                energy_feature

            ]

        )



        feature=self.normalize_vector(

            feature

        )



        # expand to 64 dimension

        embedding=np.zeros(
            self.dimension
        )


        length=min(

            len(feature),

            self.dimension

        )


        embedding[:length]=feature[:length]



        return embedding





    # =====================================================
    # Batch Encode
    # =====================================================

    def encode_objects(
        self,
        objects
    ):


        embeddings=[]



        for obj in objects:


            embeddings.append(

                self.encode_object(
                    obj
                )

            )



        return np.asarray(
            embeddings
        )
