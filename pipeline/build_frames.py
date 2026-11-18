import sys; import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from style import *
# decoy tag labels, positions in 1024 scene space
def tags(c,ox,oy,s):
    d=ImageDraw.Draw(c)
    for cx,lab,price,col in [(358,"web","$59",INK),(512,"print","$125",(17,17,17)),(657,"both","$125",INK)]:
        f1=K(int(26*s*1.0)); f2=CB(int(46*s))
        X=ox+cx*s
        w=d.textlength(lab,font=f1); d.text((X-w/2,oy+352*s),lab,font=f1,fill=col if col!=INK else DIM)
        w=d.textlength(price,font=f2); d.text((X-w/2,oy+385*s),price,font=f2,fill=col)
# Shorts
def prices(c):
    d=ImageDraw.Draw(c); f=CB(58)
    for x,t,col in [(410,"$59",INK),(540,"$125",(17,17,17)),(668,"$125",INK)]:
        w=d.textlength(t,font=f); d.text((x-w/2,1005),t,font=f,fill=col)
S=[
 ("sh1",short("s1_doorway",[[("You forgot why","ink")],[("you walked in?","ink")]],[("It's the ","ink"),("door.","key")],"Radvansky · Notre Dame · 2011")),
 ("sh2",short("s4d_eyeballs",[[("You think","ink")],[("everyone","key"),(" saw?","ink")]],[("Barely anyone.","ink")])),
 ("sh3",short("s5c_eyespop",[[("Actually?","ink")]],[("Only ","ink"),("1 in 4.","key")],"Gilovich · Cornell · 2000",tint=[(345,371,70),(517,225,70),(666,307,70)])),
 ("sh4",short("s6b_decoy",[[("One price here","ink")],[("is a ","ink"),("trap.","key")]],[("Find it.","ink")],"Ariely · MIT",tint=[(512,400,62)],fill=[(512,430)],extra=lambda c: tags(c,0,430,1080/1024))),
]
for n,c in S: c.convert("RGB").save(OUT+n+".png")
# Long-form 16:9
L=[
 ("lf1",longform("s1_doorway",[[("Doorways","key")],[("reset your","ink")],[("memory.","ink")]],"Radvansky · Notre Dame · 2011",sub="…so your brain files the old room away, along with why you came.")),
 ("lf2",longform("s4d_eyeballs",[[("The","ink")],[("spotlight","key")],[("effect","ink")]],"Gilovich · Cornell · 2000",sub="You feel like the main character. Everyone else is busy with their own shirt.")),
 ("lf4",longform("s6b_decoy",[[("The","ink")],[("decoy","key")],[("effect","ink")]],"Ariely · MIT",tint=[(512,400,62)],fill=[(512,430)],extra=lambda c: tags(c,800,0,1080/1024),sub="Nobody buys the middle one. It's there to make the bundle look cheap.")),
 ("lf3",longform("s5c_eyespop",[[("Only","ink")],[("1 in 4","key")],[("noticed.","ink")]],tint=[(345,371,70),(517,225,70),(666,307,70)],sub="Students guessed half the room would notice. It was a quarter.")),
]
for n,c in L: c.convert("RGB").save(OUT+n+".png")
# Thumbnail 1280x720
t=Image.new("RGBA",(1280,720),BG+(255,))
im,m=scene("s7_thumb",820); t.paste(im,(480,-40),m)
text_block(t,60,140,[("Your brain","ink")],118,-3,2,align="left")
text_block(t,60,290,[("lies","key"),(" to you","ink")],118,-1.5,4,align="left")
text_block(t,60,440,[("every day.","ink")],118,-2.5,6,align="left")
bug(t,40,640,30)
t.convert("RGB").save(OUT+"thumb.png")
# Avatar
a=Image.new("RGBA",(800,800),BG+(255,))
im,m=scene("s7_thumb",1100); a.paste(im.crop((150,0,950,800)),(0,40),m.crop((150,0,950,800)))
dm=Image.new("L",(800,800),0); ImageDraw.Draw(dm).ellipse((0,0,800,800),fill=255)
av=Image.new("RGBA",(800,800),(0,0,0,0)); av.paste(a,(0,0),dm); av.save(OUT+"avatar.png")
