from __future__ import division
import pygame
import math
import random
#######################################CREDITS####################################
#						SpaceRacer												 #
# 			Author of atari_boom.wav: dklon										 #
# 			Source : http://opengameart.org/content/atari-booms					 #
# 			Author of asteroids.png: phaelax 						 			 #
# 			Source : http://opengameart.org/content/asteroids		             #
#			Author of life_pickup.flac: Lamoot									 #
#			Source : http://opengameart.org/content/life-pickup-yo-frankie		 #
#			Author of soundrack.wav: FoxSynergy                                  #
#			Source: http://opengameart.org/content/soul-star                     #
#######################################CREDITS####################################
# classes & functions
def collides(image1, rect1, image2, rect2):
	mask1 = pygame.mask.from_surface(image1)
	mask2 = pygame.mask.from_surface(image2)
	dx = rect2.left - rect1.left
	dy = rect2.top - rect1.top
	return mask1.overlap(mask2, (dx,dy)) != None

def generate_asteroid(width, height):
	zone = random.choice(["north","south","east","west"])
	if zone == "north":
		return Asteroid((random.randint(0, width), 0), random.randint(181, 359))
	elif zone == "south":
		return Asteroid((random.randint(0,width),height),random.randint(1,179))
	elif zone == "west":
		return Asteroid((0,random.randint(0,height)), (270 + random.randint(1,179)) % 3)
	else:
		return Asteroid((width,random.randint(0, height)), random.randint(91,269))
	
class Spaceship(object):
	def __init__(self, position):
		self.ship = pygame.image.load("images/shuttle.png")
		self.damaged = pygame.image.load("images/damagedshuttle.png")
		self.exploded = pygame.image.load("images/explosion.png")
		self.position = position
		self.shiprect = self.ship.get_rect()
		self.explodedrect = self.exploded.get_rect()
		self.damagedrect = self.damaged.get_rect()
	
	def fire(self):
		return Missile(self.position)
	
	def move_to(self, target):
		self.position = target[0] - self.shiprect.center[0], target[1] - self.shiprect.center[1]
	
	def draw(self, screen):		
		if self.ship == self.exploded:
			screen.blit(self.exploded, (self.position[0] - (self.explodedrect.center[0]//2), self.position[1] - (self.explodedrect.center[1]//2)))
		elif self.ship == self.damaged:
			screen.blit(self.damaged, self.position)
		else:
			screen.blit(self.ship, self.position)
		
class Missile(object):
	def __init__(self, position):
		self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("images/missile.png"), (40,30)))
		self.position = position
		
	def move(self, speed):
		dx = speed * math.cos(math.radians(self.angle))
		dy = speed * math.sin(math.radians(self.angle))
		self.position = ( self.position[0] + dx, self.position[1] - dy )
	
	def on_screen(self, screen):
		rect = self.image.get_rect()
		rect.center = self.position
		return screen.get_rect().colliderect(rect)
		
	def draw(self, screen):
		rect = self.image.get_rect()
		rect.center = self.position
		screen.blit(self.image, rect)
		
	def collision_info(self):
		rect = self.image.get_rect()
		rect.center = self.position
		return (self.image, rect)
		
class Asteroid(object):
	def __init__(self, position, angle):
		asteroid = random.choice(["a1","a3","b1","b3","c1","c3","c4"])
		self.frames = []
		type = random.choice(range(0,16))
		frame = pygame.image.load("images/asteroids/%s%04d.png" % (asteroid, type))
		frame = pygame.transform.scale(frame, (160,120))
		self.frames.append(frame)
		self.frame = 0
		self.position = position
		self.angle = angle
		
	def move(self, speed):
		dx = speed * math.cos(math.radians(self.angle))
		dy = speed * math.sin(math.radians(self.angle))
		self.position = ( self.position[0] + dx, self.position[1] - dy )
			
	def rect(self):
		return self.frames[self.frame].get_rect(center = self.position)

	def on_screen(self, screen):
		return screen.get_rect().colliderect(self.rect())
		
	def draw(self, screen):
		screen.blit(self.frames[self.frame], self.rect())
		self.frame += 1
		if self.frame == len(self.frames):
			self.frame = 0	
	
class Orb(object):
	def __init__(self, position):
		self.orbs = []
		self.type = random.choice(range(1,4))
		orb = pygame.image.load("images/orb%d.png" % self.type)
		orb = pygame.transform.scale(orb, (50,50))
		self.orbs.append(orb)
		self.position = position
		
	def rect(self):
		return self.orbs[0].get_rect(center = self.position)
	
	def draw(self, screen):
		screen.blit(self.orbs[0], self.rect())
	
# set up the screen
pygame.init()
width = 800
height = 600
fps = 80
size = (width,height)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("SpaceRacer")
screenrect = screen.get_rect()
clock = pygame.time.Clock()

# background
background = pygame.image.load("images/background.png")
background2 = pygame.transform.flip(background, False, True)
backrect = background.get_rect(bottomleft = screenrect.bottomleft)
backrect2 = background2.get_rect(bottomleft = backrect.topleft)
backrect3 = backrect.copy()
backrect3.bottomleft = backrect2.topleft
soundtrack = pygame.mixer.Sound("sounds/Bish.wav")
boom = pygame.mixer.Sound("sounds/atari_boom.wav")
healthup = pygame.mixer.Sound("sounds/life_pickup.flac")
soundtrack.set_volume(1)
soundtrack.play(-1)
boom.set_volume(0.1)
healthup.set_volume(1)

# set up objects
ship = Spaceship(screenrect.center)
shiprect = ship.shiprect.copy()
shiprect.topleft = ship.position
asteroids = []
orbs = []
drawn = []
counter = 0
difficulty = 1
level = 1
points = 0
score = 0
health = 25
damage = -1
lost = False
won = False
done = False
#----------INTRO------------#
while not done:
	clock.tick(fps)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			exit()
		elif event.type == pygame.MOUSEBUTTONDOWN:
			done = True
	screen.fill((255,255,255))
	screen.blit(pygame.font.SysFont("microsoftsansserif", 80, False, False).render(("SpaceRacer"), True, (0,0,0)), (screenrect.center[0] - 300, screenrect.center[1] - 50))
	screen.blit(pygame.font.SysFont("microsoftsansserif", 50, False, False).render(("Click to play!"), True, (155,155,155)), (screenrect.center[0] - 75, screenrect.center[1] + 50))
	pygame.display.flip()
#----------MAIN LOOP--------#
while True:
	#	set-up events
	if score < 0:
		score = 0
	clock.tick(fps)
	counter += 1
	if counter == 2 * fps:
		difficulty += 1
		counter = 0
		if difficulty == level + 3:
			level += 1
			difficulty = level
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			exit()
		elif event.type == pygame.MOUSEMOTION:
			if ship.ship != ship.exploded:
				ship.move_to(event.pos)
				shiprect.center = event.pos
	# on-screen objects		
	pygame.mouse.set_visible(lost or won)
	# background
	if backrect2.top > height:
		backrect.bottomleft = screenrect.bottomleft
		backrect2.bottomleft = backrect.topleft
		backrect3.bottomleft = backrect2.topleft
	else:
		backrect.bottomleft = (backrect.bottomleft[0], backrect.bottomleft[1] + level)
		backrect2.bottomleft = (backrect2.bottomleft[0], backrect2.bottomleft[1] + level)
		backrect3.bottomleft = (backrect3.bottomleft[0], backrect3.bottomleft[1] + level)
	screen.blit(background, backrect)
	screen.blit(background2, backrect2)
	screen.blit(background, backrect3)
	# ship
	ship.draw(screen)
	if health > 15:
		ship.ship = pygame.image.load("images/shuttle.png")
	# asteroids
	for asteroid in asteroids:
		asteroid.draw(screen)
		asteroid.move(1+level)
		if collides(ship.ship, shiprect, asteroid.frames[asteroid.frame], asteroid.rect()) and not lost:
			score -= 100
			damage += 1
			if health == 0:
				ship.ship = ship.exploded
				ship.shiprect = ship.explodedrect
				soundtrack.stop()
				boom.play(0)
				lost = True
			elif health <= 15:
				ship.ship = ship.damaged
				boom.play(0)
				health -= 1
			else:
				boom.play(0)
				health -= 1
	asteroids = [ asteroid for asteroid in asteroids if asteroid.on_screen(screen) ]
	
	# TODO add if collides(bullet, bulletrect, asteroid.frames[asteroid.frame], asteroid.rect()): 
	
	
	while len(asteroids) < 2 * difficulty and not won:
		asteroids.append(generate_asteroid(width,height))
	# orbs
	for orb in orbs:
		orb.draw(screen)
		if collides(ship.ship, shiprect, orb.orbs[0], orb.rect()):
			orbs.remove(orb)
			healthup.play(0)
			health += 5
			score += 1234
	if level % 3 == 0 and len(drawn) < level // 3 :
		orbs.append(Orb((random.choice(range(26,width-26)),random.choice(range(26,height-26)))))
		drawn.append(orbs[0])
	# Everything else
	if lost:
		screen.blit(pygame.font.SysFont("microsoftsansserif", 30, False, False).render(("BOOM! Top speed: %d000 Km/M Distance: %d Km(s)" % (level,points)), True, (255,0,0)), screenrect.midleft)
		screen.blit(pygame.font.SysFont("microsoftsansserif", 30, False, False).render(("Total points: %d" % (score)), True, (255,255,0)), (screenrect.midtop[0] - 100, screenrect.midtop[1] + 100))
		screen.blit(pygame.font.SysFont("microsoftsansserif", 30, False, False).render(("Orbs collected: %d" % (len(drawn) - len(orbs))), True, (255,255,255)), (screenrect.bottomright[0] - 300,screenrect.bottomright[1] - 40))
		screen.blit(pygame.font.SysFont("microsoftsansserif", 30, False, False).render(("Damage Taken: %d" % damage), True, (255,0,0)), (screenrect.bottomleft[0],screenrect.bottomleft[1]-40))
		clock.tick(1)
	else:
		points += 1 * level
		score += 3 * level
		screen.blit(pygame.font.SysFont("microsoftsansserif", 25, False, False).render(("Level %d " % level), True, (155,155,155)), screenrect.topleft)
		screen.blit(pygame.font.SysFont("microsoftsansserif", 20, False, False).render(("Travelled: %d Km" % points), True, (255,255,255)), (screenrect.bottomleft[0],screenrect.bottomleft[1]-30))
		screen.blit(pygame.font.SysFont("microsoftsansserif", 30, False, False).render(("Health: %d" % health), True, (0,255,0)), (screenrect.midtop[0] - 75,screenrect.midtop[1]))
		screen.blit(pygame.font.SysFont("microsoftsansserif", 30, False, False).render(("Score: %d" % score), True, (255,255,0)), (screenrect.bottomright[0] - 250,screenrect.bottomright[1] - 40))

	if level == 12 and difficulty == level + 2:
		screen.blit(pygame.font.SysFont("microsoftsansserif", 60, False, False).render(("YOU WIN!"), True, (255,255,0)), screenrect.midleft)
		clock.tick(1)
		won = True
	pygame.display.flip()