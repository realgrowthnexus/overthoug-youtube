from PIL import Image, ImageDraw, ImageFont, ImageOps
import math
F="/home/user/overthoug-youtube/style/fonts/"
def whiten(im,th=232):
    im=im.convert('RGB'); px=im.load()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b=px[x,y]
            if r>th and g>th and b>th: px[x,y]=(255,255,255)
    return im
def arrow(d,start,end,bend=-60,w=6):
    (x0,y0),(x1,y1)=start,end; mx,my=(x0+x1)/2,(y0+y1)/2+bend
    pts=[((1-t)**2*x0+2*(1-t)*t*mx+t*t*x1,(1-t)**2*y0+2*(1-t)*t*my+t*t*y1) for t in [i/40 for i in range(41)]]
    d.line(pts,fill='black',width=w,joint='curve')
    ax,ay=pts[-1]; bx,by=pts[-4]; a=math.atan2(ay-by,ax-bx)
    for s in (2.5,-2.5):
        d.line([(ax,ay),(ax-34*math.cos(a+s/5),ay-34*math.sin(a+s/5))],fill='black',width=w)
def thumb(src,out,small,big,arrow_to,dx=-20):
    W,H=1280,720; c=Image.new('RGB',(W,H),'white')
    im=whiten(Image.open(src)).resize((800,800)); c.paste(im,(dx,-40))
    d=ImageDraw.Draw(c)
    fs=ImageFont.truetype(F+"Kalam-Bold.ttf",78); fb=ImageFont.truetype(F+"Kalam-Bold.ttf",150)
    fb=ImageFont.truetype(F+"Kalam-Bold.ttf",140); cx=1030
    d.text((cx,290),small,font=fs,fill='black',anchor='mm')
    for i,l in enumerate(big.split()): d.text((cx,415+i*135),l,font=fb,fill='black',anchor='mm')
    arrow(d,(cx-40,205),arrow_to,bend=-70)
    c.save(out,quality=92)
def frame(src,out,caption=None):
    W,H=1920,1080; c=Image.new('RGB',(W,H),'white')
    im=whiten(Image.open(src)).resize((1080,1080)); c.paste(im,((W-1080)//2,0))
    if caption:
        d=ImageDraw.Draw(c); f=ImageFont.truetype(F+"Kalam-Bold.ttf",64)
        d.text((W//2,120),caption,font=f,fill='black',anchor='mm')
    c.save(out,quality=92)
thumb('t1b_sweep.jpg','THUMB_chimney_sweep.jpg','6 years old','Stuck Inside',(640,260))
thumb('t2b_executioner.jpg','THUMB_executioner.jpg','Everyone','Hates You',(560,250),dx=-160)
frame('s1b_born.jpg','FRAME1_born.jpg','London, 1841')
frame('s2b_sold.jpg','FRAME2_sold.jpg','Sold to a master sweep')
frame('s3b_climb.jpg','FRAME3_climb.jpg')
