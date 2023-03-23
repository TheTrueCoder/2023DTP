<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.9" tiledversion="1.9.2" name="ItemsAndTraps" tilewidth="32" tileheight="32" tilecount="7" columns="0">
 <grid orientation="orthogonal" width="1" height="1"/>
 <tile id="0">
  <image width="16" height="16" source="Block1.png"/>
 </tile>
 <tile id="1">
  <image width="16" height="16" source="miniSuriken.png"/>
 </tile>
 <tile id="2">
  <image width="16" height="16" source="PushBox.png"/>
 </tile>
 <tile id="3">
  <image width="16" height="16" source="Rock.png"/>
 </tile>
 <tile id="4">
  <image width="32" height="32" source="Spike2.png"/>
 </tile>
 <tile id="5">
  <image width="32" height="24" source="StaticSpike.png"/>
  <animation>
   <frame tileid="3" duration="100"/>
   <frame tileid="2" duration="100"/>
   <frame tileid="1" duration="100"/>
   <frame tileid="5" duration="100"/>
   <frame tileid="6" duration="100"/>
  </animation>
 </tile>
 <tile id="6">
  <image width="32" height="32" source="Suriken.png"/>
 </tile>
</tileset>
