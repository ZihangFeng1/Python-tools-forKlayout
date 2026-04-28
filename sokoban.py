# sokoban.py - converted from Ruby to Python using Klayout pya API
import pya
import math


class MenuHandler(pya.Action):
    def __init__(self, t, k, action):
        self.title = t
        self.shortcut = k
        self._action = action

    def triggered(self):
        self._action(self)

    _action = None


class GameObject:
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._cell_index = None

    def create_cell(self, game, name):
        if game.layout.has_cell(name):
            self._cell_index = game.layout.cell_by_name(name)
        else:
            self._cell_index = game.layout.add_cell(name)
            self.build_cell(game)

    def instantiate(self, game):
        t = pya.Trans(pya.Point(self._x * 1000, self._y * 1000))
        inst = pya.CellInstArray(self._cell_index, t)
        game.topcell().insert(inst)

    def can_move(self, level, x, y):
        return True

    def is_at(self, x, y):
        return x == self._x and y == self._y

    def is_guy(self):
        return False

    def is_obstacle(self):
        return False

    def is_target(self):
        return False

    def is_diamond(self):
        return False


class Wall(GameObject):
    def construct(self, game):
        self.create_cell(game, "wall")

    def build_cell(self, game):
        lay1 = game.create_layer("wall.1", 0x800000, 0x404040, 0)

        ystep = 125
        width = 250
        for n in range(int(1000 / ystep)):
            x = -width / 2 if (n % 2 == 1) else 0
            while x < 1000:
                brick = pya.Box(
                    max(x, 0), n * ystep,
                    min(x + width, 1000), (n + 1) * ystep)
                game.layout.cell(self._cell_index).shapes(lay1).insert_box(brick)
                x += width

    def is_obstacle(self):
        return True


class Target(GameObject):
    def construct(self, game):
        self.create_cell(game, "target")

    def build_cell(self, game):
        lay2 = game.create_layer("target.2", 0x008000, 0x008000, 0)
        lay1 = game.create_layer("target.1", 0x40ff40, 0x00ff00, 0)

        rings = [[0, 50, lay1], [50, 100, lay2], [100, 150, lay1],
                 [150, 200, lay2], [200, 250, lay1], [250, 300, lay2],
                 [300, 350, lay1]]
        for r in rings:
            pointlist = []
            n = 32
            for a in range(n):
                x = 500 + r[1] * math.cos((2 * math.pi * a) / n)
                y = 500 + r[1] * math.sin((2 * math.pi * a) / n)
                pointlist.append(pya.Point(x, y))
            shape = pya.Polygon(pointlist)
            if r[0] > 0:
                pointlist = []
                n = 32
                for a in range(n):
                    x = 500 + r[0] * math.cos((2 * math.pi * a) / n)
                    y = 500 + r[0] * math.sin((2 * math.pi * a) / n)
                    pointlist.append(pya.Point(x, y))
                shape.insert_hole(pointlist)
            game.layout.cell(self._cell_index).shapes(r[2]).insert_polygon(shape)

    def is_target(self):
        return True


class Diamond(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self._in_target = False

    def construct(self, game):
        self.create_cell(game, "diamond")

    def build_cell(self, game):
        lay1 = game.create_layer("diamond.1", 0x80ff80, 0x404040, 0)

        pts = [
            [[300, 900], [700, 900], [600, 870], [400, 870]],
            [[700, 900], [900, 730], [680, 800], [600, 870]],
            [[680, 800], [900, 730], [660, 520], [600, 720]],
            [[660, 520], [600, 720], [400, 720], [340, 520]],
            [[320, 800], [100, 730], [340, 520], [400, 720]],
            [[300, 900], [100, 730], [320, 800], [400, 870]],
            [[400, 870], [600, 870], [680, 800], [600, 720],
             [400, 720], [320, 800]],
            [[100, 730], [500, 125], [340, 520]],
            [[340, 520], [500, 125], [660, 520]],
            [[660, 520], [500, 125], [900, 730]]]

        for pp in pts:
            pointlist = [pya.Point(p[0], p[1]) for p in pp]
            shape = pya.Polygon(pointlist)
            game.layout.cell(self._cell_index).shapes(lay1).insert_polygon(shape)

    def can_move(self, level, x, y):
        for o in level._objs:
            if o.is_at(self._x + x, self._y + y):
                if o.is_obstacle() or o.is_diamond():
                    return False
        return True

    def move(self, level, x, y):
        self._x += x
        self._y += y
        self._in_target = False
        for o in level._objs:
            if o.is_target() and o.is_at(self._x, self._y):
                self._in_target = True

    def is_diamond(self):
        return True

    def in_target(self):
        return self._in_target


class Guy(GameObject):
    def construct(self, game):
        self.create_cell(game, "guy")

    def build_cell(self, game):
        lay1 = game.create_layer("guy.1", 0x806000, 0x604000, 0)

        pts = [[[400, 880], [420, 940], [580, 940], [600, 880],
                [550, 750], [450, 750]],
               [[350, 740], [630, 740], [710, 640], [710, 350],
                [630, 350], [630, 610], [620, 610], [620, 100],
                [700, 100], [700, 50], [505, 50], [505, 400],
                [495, 400], [495, 50], [300, 50], [300, 100],
                [380, 100], [380, 610], [370, 610], [370, 350],
                [290, 350], [290, 640]]]

        for pp in pts:
            pointlist = [pya.Point(p[0], p[1]) for p in pp]
            shape = pya.Polygon(pointlist)
            game.layout.cell(self._cell_index).shapes(lay1).insert_polygon(shape)

    def can_move(self, level, x, y):
        for o in level._objs:
            if o.is_at(self._x + x, self._y + y):
                if o.is_obstacle():
                    return False
                elif o.is_diamond() and not o.can_move(level, x, y):
                    return False
        return True

    def move(self, level, x, y):
        self._x += x
        self._y += y
        for o in level._objs:
            if o.is_at(self._x, self._y) and o.is_diamond():
                o.move(level, x, y)
        return True

    def is_guy(self):
        return True


class Level:
    def __init__(self):
        arena = [
            '   ####',
            '####  #',
            '#     ####',
            '# $ #  . ##',
            '#  #   .  #',
            '#  #$$#.  #',
            '#     #####',
            '# @ ###',
            '#   #',
            '#####',
        ]

        self._objs = []

        y = len(arena) - 1
        for line in arena:
            x = 0
            for o in line:
                if o == '#':
                    self._objs.append(Wall(x, y))
                elif o == '.':
                    self._objs.append(Target(x, y))
                elif o == '$':
                    self._objs.append(Diamond(x, y))
                elif o == '@':
                    guy = Guy(x, y)
                    self._guy = guy
                    self._objs.append(guy)
                x += 1
            y -= 1

    def each_object(self, action):
        for o in self._objs:
            action(o)

    def guy(self):
        return self._guy


class Game:
    def __init__(self):
        app = pya.Application.instance()
        mw = app.main_window()
        menu = mw.menu()

        def move_down():
            self.move(0, -1)
        def move_left():
            self.move(-1, 0)
        def move_right():
            self.move(1, 0)
        def move_up():
            self.move(0, 1)
        def restart_game():
            self.restart()

        self._down_handler = MenuHandler("Down", "Down", lambda s: move_down())
        self._left_handler = MenuHandler("Left", "Left", lambda s: move_left())
        self._right_handler = MenuHandler("Right", "Right", lambda s: move_right())
        self._up_handler = MenuHandler("Up", "Up", lambda s: move_up())
        self._restart_handler = MenuHandler("Restart", "", lambda s: restart_game())

        menu.insert_separator("@toolbar.end", "name")
        menu.insert_item("@toolbar.end", "sokoban_down", self._down_handler)
        menu.insert_item("@toolbar.end", "sokoban_left", self._left_handler)
        menu.insert_item("@toolbar.end", "sokoban_right", self._right_handler)
        menu.insert_item("@toolbar.end", "sokoban_up", self._up_handler)
        menu.insert_item("@toolbar.end", "sokoban_restart", self._restart_handler)

        mw.create_layout("", 0)
        self._view = mw.current_view()
        self._layout = self._view.cellview(0).layout()
        self._topcell = self._layout.add_cell("game")

        self._layers = {}

        dummy_objs = [Wall(0, 0), Target(0, 0), Diamond(0, 0), Guy(0, 0)]
        for o in dummy_objs:
            o.construct(self)

        self._level = Level()
        self._level.each_object(lambda o: o.construct(self))
        self._level.each_object(lambda o: o.instantiate(self))

        self._view.select_cell_path([self._topcell], 0)
        self._view.update_content()
        self._view.zoom_fit()
        self._view.max_hier()

    def restart(self):
        self._level = Level()
        self._level.each_object(lambda o: o.construct(self))
        self.redraw()

    def redraw(self):
        self._view.stop_redraw()
        self.topcell().clear_insts()
        self._level.each_object(lambda o: o.instantiate(self))
        self._view.select_cell_path([self._topcell], 0)
        self._view.update_content()
        pya.Application.instance().main_window().redraw()

    def move(self, dx, dy):
        if not self._view.destroyed():
            if self._level.guy().can_move(self._level, dx, dy):
                self._level.guy().move(self._level, dx, dy)

            self.redraw()

            all_in_target = True
            for o in self._level._objs:
                if o.is_diamond() and not o.in_target():
                    all_in_target = False
            if all_in_target:
                pya.MessageBox.info("Done", "Congratulations! Level done.",
                                    pya.MessageBox.b_ok)
                self._level = Level()
                self._level.each_object(lambda o: o.construct(self))
                self.redraw()

    def topcell(self):
        return self._layout.cell(self._topcell)

    @property
    def layout(self):
        return self._layout

    def create_layer(self, name, color, frame_color, stipple):
        if name not in self._layers:
            linfo = pya.LayerInfo()
            lid = self._layout.insert_layer(linfo)
            self._layers[name] = lid

            lpp = self._view.end_layers()
            ln = pya.LayerPropertiesNode()
            ln.dither_pattern = stipple
            ln.fill_color = color
            ln.frame_color = frame_color
            ln.width = 1
            ln.source_layer_index = lid
            self._view.insert_layer(lpp, ln)
        else:
            lid = self._layers[name]

        return lid


if __name__ == "__main__":
    game = Game()
    pya.Application.instance().exec_()
