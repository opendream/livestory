class Scour:
    
    def __init__(self, nx, ny, width, height, gap):
        self.pw = (width+gap)/nx
        self.ph = (height+gap)/ny
        self.gap = gap
    
    def get_rect_list(self):
        return [
            ((2, 3), (5, 5)),
            ((0, 1), (1, 4)),
            ((6, 3), (7, 5)),
            ((2, 1), (3, 2)),
            ((5, 6), (6, 7)),
            ((8, 3), (9, 4)),
            ((5, 2), (6, 2)),
            ((4, 1), (4, 2)),
            ((1, 5), (1, 6)),
            ((7, 6), (8, 6)),
            ((7, 7), (7, 8)),
            ((8, 1), (8, 2)),
            ((2, 0), (2, 0)),
            ((3, 0), (3, 0)),
            ((4, 0), (4, 0)),
            ((5, 1), (5, 1)),
            ((6, 1), (6, 1)),
            ((8, 5), (8, 5)),
            ((9, 6), (9, 6)),
            ((8, 7), (8, 7)),
            ((4, 6), (4, 6)),
            ((3, 6), (3, 6)),
            ((2, 6), (2, 6)),
            ((1, 7), (1, 7)),
            ((7, 2), (7, 2))
        ]
        
    def get_rect(self):
        rects = []    
        for (x1, y1), (x2, y2) in self.get_rect_list():
            _left = x1*self.pw
            _right = y1*self.ph
            _width = (x2-x1+1)*self.pw-self.gap
            _height = (y2-y1+1)*self.ph-self.gap
            rects.append({
                'left': _left,
                'top': _right,
                'width': _width,
                'height': _height,
                'widthxheight': '%sx%s' % (_width, _height),
                'placement': 'right' if _left <= _width/2 else 'left'
            })
        return rects