from balltracker import point_dist

class Binfo:
    def __init__(self, fr, x, y):
        self.fr = fr
        self.x = x
        self.y = y
        self.move = False
    def print(self):
        return f'({self.fr}, {self.x}, {self.y}, {self.move})'



class Ball:
    def __init__(self):
        self.ball_list = []
        self.modified_ball_list = []
        self.id = None
        self.last_event_obj = None
        self.event_frame = []
        self.last_csh_dist = 35

    def insert_obj(self, obj):
        self.ball_list.append(obj)
    
    def check_move(self, index):
        margin = 2.24
        if index < 2:
            return False
        t = index - 2
        dist = point_dist(self.ball_list[index], self.ball_list[t])
        
        while t > 0:
            if self.ball_list[t].move == True or dist > margin:
                break
            else:
                t -= 1
                dist = point_dist(self.ball_list[index], self.ball_list[t])
        return False if dist <= margin else True

    def add_move(self):
        for i in range(len(self.ball_list)):
            self.ball_list[i].move = self.check_move(i)

    def insert_predict(self, fr, x, y, index):
        b = Binfo(fr, x, y)
        self.modified_ball_list.insert(index, b)
        return b

    def find_index(self, tar_frame):
        i = 0
        while self.modified_ball_list[i].fr < tar_frame:
            i += 1
        return i

    def add_event(self, obj1_id, obj2_id, event_frame, dist):
        if self.id == obj1_id:
            self.last_event_obj = obj2_id
            self.event_frame.append(event_frame)
            if obj2_id in range(1, 5):
                self.last_csh_dist = dist
    
    def update_csh_event(self, fr_old, fr_new):
        event_idx = self.event_frame.index(fr_old)
        self.event_frame[event_idx] = fr_new
        self.event_frame.sort()

    def delete_event(self, obj1_id):
        if self.id == obj1_id:
            del self.event_frame[-1]

    def print(self):
        for b in self.modified_ball_list:
            print(b.fr, b.x, b.y, b.move)