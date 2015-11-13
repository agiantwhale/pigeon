+++
date = "2015-11-12T21:28:42-05:00"
title = "Vision Improvements"

+++

I had terrible accuracy when there was motion blur in the video source. My attempt to solve this issue by blurring the positive training set and retraining them.

It works fairly well. (Left is the previous extractor, right is the new extractor trained from blurred images.)

![Imgur](http://i.imgur.com/auMfAso.png)
![Imgur](http://i.imgur.com/o4RQpHV.png)
![Imgur](http://i.imgur.com/NraKfsQ.png)
![Imgur](http://i.imgur.com/usUkqm5.png)

**However, for strongly blurred images, it still falls short.**

![Imgur](http://i.imgur.com/Psjupmb.png)

Next idea is to apply deblurring filters before running detection. Adobe released some information regarding this, I will take a look later next weekend.
