import math

import pico2d
from transitions import Machine

class Boy:
    IDLE = 'IDLE'
    RUN = 'RUN'
    SLEEP = 'SLEEP'
    IDLE_DURATION = 5.0
    RUN_SPEED = 10
    FRAME_WIDTH = 100
    SCREEN_WIDTH = 800
    MIN_X = FRAME_WIDTH // 2
    MAX_X = SCREEN_WIDTH - FRAME_WIDTH // 2
    SLEEP_ANGLE = math.pi / 2

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.pressed_directions = set()
        self.image = pico2d.load_image('animation_sheet.png')
        self.state: str = self.IDLE
        self.sleep_angle = -self.SLEEP_ANGLE
        self.idle_started_at = pico2d.get_time()
        self.state_machine = Machine(
            model=self,
            states=[self.IDLE, self.RUN, self.SLEEP],
            initial=self.IDLE,
            auto_transitions=False,
        )
        self.state_machine.add_transition(
            trigger='run',
            source=[self.IDLE, self.SLEEP],
            dest=self.RUN,
            after='_enter_run',
        )
        self.state_machine.add_transition(
            trigger='stop_running',
            source=self.RUN,
            dest=self.IDLE,
            after='_reset_idle_timer',
        )
        self.state_machine.add_transition(
            trigger='sleep',
            source=self.IDLE,
            dest=self.SLEEP,
            after='_enter_sleep',
        )
        self.state_machine.add_transition(
            trigger='wake_up',
            source=self.SLEEP,
            dest=self.IDLE,
            after='_reset_idle_timer',
        )

    def update(self):
        if self.state == self.IDLE:
            if pico2d.get_time() - self.idle_started_at >= self.IDLE_DURATION:
                self.sleep()
                return
            self.frame = (self.frame + 1) % 8

        elif self.state == self.RUN:
            self.x += self.RUN_SPEED * self.face_dir
            self.x = max(self.MIN_X, min(self.x, self.MAX_X))
            self.frame = (self.frame + 1) % 8

    def handle_event(self, event):
        if event.type == pico2d.SDL_KEYDOWN:
            if (event.key == pico2d.SDLK_SPACE
                    and self.state == self.SLEEP):
                self.wake_up()
            elif (event.key in (pico2d.SDLK_LEFT, pico2d.SDLK_RIGHT)
                  and self.state in (self.IDLE, self.SLEEP)):
                self.pressed_directions.add(event.key)
                self.face_dir = -1 if event.key == pico2d.SDLK_LEFT else 1
                if self.state in (self.IDLE, self.SLEEP):
                    self.run()
        elif (event.type == pico2d.SDL_KEYUP
              and event.key in self.pressed_directions):
            self.pressed_directions.remove(event.key)
            if self.state == self.RUN and not self.pressed_directions:
                self.stop_running()

    def _enter_sleep(self):
        self.frame = 0
        self.sleep_angle = (
            self.SLEEP_ANGLE if self.face_dir == 1 else -self.SLEEP_ANGLE
        )

    def _enter_run(self):
        self.frame = 0

    def _reset_idle_timer(self):
        self.idle_started_at = pico2d.get_time()
        self.frame = 0

    def draw(self):
        if self.state == self.RUN:
            clip_y = 100 if self.face_dir == 1 else 0
        elif self.face_dir == 1:
            clip_y = 300
        else:
            clip_y = 200

        frame = self.frame if self.state in (self.IDLE, self.RUN) else 0
        if self.state == self.SLEEP:
            self.image.clip_composite_draw(
                frame * 100,
                clip_y,
                100,
                100,
                self.sleep_angle,
                '',
                self.x,
                self.y-25,
                100,
                100,
            )
        else:
            self.image.clip_draw(frame * 100, clip_y, 100, 100, self.x, self.y)
