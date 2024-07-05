
class WristCursor:

    def __init__(self, wrist, cursor):
        self.wrist = wrist
        self.cursor = cursor

        
        self.normalized_wrist_coordinates = (0, 0)
        self.normalized_cursor_coordinates = (0, 0)


    def update(self):
        self.cursor.x = self.wrist.x
        self.cursor.y = self.wrist.y