class InputValidator:
    """
    コンソール入力のバリデーションを担当するクラス。
    """

    @staticmethod
    def get_positive_float(message: str) -> float:
        """
        0より大きい数値が入力されるまで繰り返す。
        """

        while True:
            input_value = input(message)

            try:
                value = float(input_value)

                if value <= 0:
                    print("0より大きい数値を入力してください。")
                    continue

                return value

            except ValueError:
                print("数値を入力してください。")

    @staticmethod
    def get_launch_angle(message: str) -> float:
        """
        0より大きく、90以下の角度が入力されるまで繰り返す。
        """

        while True:
            input_value = input(message)

            try:
                angle = float(input_value)

                if angle <= 0 or angle > 90:
                    print("発射角度は0より大きく90度以下で入力してください。")
                    continue

                return angle

            except ValueError:
                print("数値を入力してください。")