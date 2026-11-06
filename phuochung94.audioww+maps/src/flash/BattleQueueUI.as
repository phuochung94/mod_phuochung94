package
{
   import flash.events.Event;
   import flash.display.Sprite;
   import flash.display.DisplayObject;
   import flash.geom.Point;
   import flash.text.TextField;
   import flash.text.TextFormat;
   import flash.text.TextFormatAlign;
   import flash.utils.Dictionary;
   import net.wg.gui.lobby.battlequeue.BattleQueue;
   
   [Embed(source="/_assets/assets.swf", symbol="symbol102")]
   public dynamic class BattleQueueUI extends BattleQueue
   {
      
      public var __setPropDict:Dictionary = new Dictionary(true);
      
      public var __lastFrameProp:int = -1;
      
      public function BattleQueueUI()
      {
         addFrameScript(0,this.frame1,1,this.frame2,2,this.frame3,3,this.frame4,4,this.frame5,5,this.frame6,6,this.frame7);
         super();
         addEventListener(Event.FRAME_CONSTRUCTED,this.__setProp_handler,false,0,true);
         addEventListener(Event.ENTER_FRAME, this.updateCompactQueue, false, 0, true);
      }
      
      internal function __setProp_listByType_BattleQueueUI_listByType_0(param1:int) : *
      {
         if(listByType != null && param1 >= 1 && param1 <= 7 && (this.__setPropDict[listByType] == undefined || !(int(this.__setPropDict[listByType]) >= 1 && int(this.__setPropDict[listByType]) <= 7)))
         {
            this.__setPropDict[listByType] = param1;
            try
            {
               listByType["componentInspectorSetting"] = true;
            }
            catch(e:Error)
            {
            }
            listByType.UIID = 18219011;
            listByType.enabled = true;
            listByType.enableInitCallback = false;
            listByType.focusable = false;
            listByType.itemRendererName = "BattleQueueItemRendererUI";
            listByType.itemRendererInstanceName = "";
            listByType.margin = 0;
            listByType.inspectablePadding = {
               "top":0,
               "right":0,
               "bottom":0,
               "left":0
            };
            listByType.rowHeight = 48;
            listByType.scrollBar = "";
            listByType.useRightButton = false;
            listByType.useRightButtonForSelect = false;
            listByType.visible = true;
            listByType.wrapping = "stick";
            try
            {
               listByType["componentInspectorSetting"] = false;
            }
            catch(e:Error)
            {
            }
         }
      }
      
      internal function __setProp_startButton_BattleQueueUI_startButton_0(param1:int) : *
      {
         if(startButton != null && param1 >= 1 && param1 <= 7 && (this.__setPropDict[startButton] == undefined || !(int(this.__setPropDict[startButton]) >= 1 && int(this.__setPropDict[startButton]) <= 7)))
         {
            this.__setPropDict[startButton] = param1;
            try
            {
               startButton["componentInspectorSetting"] = true;
            }
            catch(e:Error)
            {
            }
            startButton.UIID = 18219010;
            startButton.autoRepeat = false;
            startButton.autoSize = "none";
            startButton.data = "";
            startButton.inspectableDisabledFillPadding = {
               "top":0,
               "right":0,
               "bottom":0,
               "left":0
            };
            startButton.enabled = true;
            startButton.enableInitCallback = false;
            startButton.focusable = true;
            startButton.helpDirection = "T";
            startButton.helpText = "";
            startButton.label = "#menu:prebattle/startButton";
            startButton.paddingHorizontal = 5;
            startButton.selected = false;
            startButton.soundId = "";
            startButton.soundType = "buttonCaps";
            startButton.toggle = false;
            startButton.tooltip = "";
            startButton.visible = true;
            try
            {
               startButton["componentInspectorSetting"] = false;
            }
            catch(e:Error)
            {
            }
         }
      }
      
      internal function __setProp_exitButton_BattleQueueUI_exitButton_0(param1:int) : *
      {
         if(exitButton != null && param1 >= 1 && param1 <= 7 && (this.__setPropDict[exitButton] == undefined || !(int(this.__setPropDict[exitButton]) >= 1 && int(this.__setPropDict[exitButton]) <= 7)))
         {
            this.__setPropDict[exitButton] = param1;
            try
            {
               exitButton["componentInspectorSetting"] = true;
            }
            catch(e:Error)
            {
            }
            exitButton.UIID = 18219009;
            exitButton.autoRepeat = false;
            exitButton.autoSize = "none";
            exitButton.data = "";
            exitButton.inspectableDisabledFillPadding = {
               "top":0,
               "right":0,
               "bottom":0,
               "left":0
            };
            exitButton.enabled = true;
            exitButton.enableInitCallback = false;
            exitButton.focusable = true;
            exitButton.helpDirection = "T";
            exitButton.helpText = "";
            exitButton.label = "#menu:prebattle/exitButton";
            exitButton.paddingHorizontal = 5;
            exitButton.selected = false;
            exitButton.soundId = "";
            exitButton.soundType = "buttonCaps";
            exitButton.toggle = false;
            exitButton.tooltip = "";
            exitButton.visible = true;
            try
            {
               exitButton["componentInspectorSetting"] = false;
            }
            catch(e:Error)
            {
            }
         }
      }
      
      internal function __setProp_handler(param1:Object) : *
      {
         var _loc2_:int = int(currentFrame);
         if(this.__lastFrameProp == _loc2_)
         {
            return;
         }
         this.__lastFrameProp = _loc2_;
         this.__setProp_listByType_BattleQueueUI_listByType_0(_loc2_);
         this.__setProp_startButton_BattleQueueUI_startButton_0(_loc2_);
         this.__setProp_exitButton_BattleQueueUI_exitButton_0(_loc2_);
      }
      
      private var compactQueue:Sprite;
      private var searchingText:TextField;
      private var elapsedText:TextField;
      private var randomText:TextField;
      private var waitingText:TextField;

      private function makeQueueText(size:int, color:uint, top:int):TextField
      {
         var label:TextField = new TextField();
         label.width = 420;
         label.height = 38;
         label.x = -210;
         label.y = top;
         label.selectable = false;
         label.mouseEnabled = false;
         var format:TextFormat = new TextFormat("$TitleFont", size, color);
         format.align = TextFormatAlign.CENTER;
         label.defaultTextFormat = format;
         compactQueue.addChild(label);
         return label;
      }

      private function updateCompactQueue(event:Event):void
      {
         if(stage == null || modeTitle == null || timerText == null || exitButton == null)
         {
            return;
         }
         var marker:String = modeTitle.text;
         if(marker.indexOf("MOD_QUEUE_") < 0)
         {
            return;
         }
         var vietnamese:Boolean = marker.indexOf("MOD_QUEUE_VI") >= 0;
         if(compactQueue == null)
         {
            compactQueue = new Sprite();
            compactQueue.mouseEnabled = false;
            compactQueue.graphics.lineStyle(1, 0xa56b3b, 0.9);
            compactQueue.graphics.beginFill(0x742811, 0.97);
            compactQueue.graphics.drawRect(-145, 0, 290, 52);
            compactQueue.graphics.endFill();
            compactQueue.graphics.lineStyle(1, 0xffbe6b, 0.45);
            compactQueue.graphics.moveTo(-140, 3);
            compactQueue.graphics.lineTo(140, 3);
            compactQueue.graphics.lineStyle(2, 0xa37542, 0.7);
            compactQueue.graphics.moveTo(-110, 67);
            compactQueue.graphics.lineTo(110, 67);
            searchingText = makeQueueText(23, 0xf4e7ce, 9);
            elapsedText = makeQueueText(28, 0xf2f2e9, 77);
            randomText = makeQueueText(17, 0xccbda5, 115);
            waitingText = makeQueueText(14, 0xb0aca5, 144);
            addChild(compactQueue);
         }
         for(var i:int = 0; i < numChildren; i++)
         {
            var child:DisplayObject = getChildAt(i);
            if(child != compactQueue && child != DisplayObject(exitButton))
            {
               child.visible = false;
            }
         }
         compactQueue.visible = true;
         var location:Point = globalToLocal(new Point(stage.stageWidth / 2, 18));
         compactQueue.x = location.x;
         compactQueue.y = location.y;
         searchingText.text = vietnamese ? "ĐANG TÌM TRẬN…" : "SEARCHING…";
         elapsedText.text = timerText.text;
         randomText.text = vietnamese ? "TRẬN NGẪU NHIÊN" : "RANDOM BATTLE";
         var count:Array = playersLabel.text.match(/[0-9][0-9 ,.]*[0-9]|[0-9]/);
         waitingText.text = count != null ? count[0] + (vietnamese ? " người đang chờ" : " players in queue") : "";
         exitButton.label = vietnamese ? "HỦY TÌM TRẬN" : "CANCEL SEARCH";
         exitButton.x = location.x - exitButton.width / 2;
         exitButton.y = location.y + 183;
      }

      override protected function onDispose():void
      {
         removeEventListener(Event.ENTER_FRAME, this.updateCompactQueue);
         if(compactQueue != null)
         {
            removeChild(compactQueue);
            compactQueue = null;
         }
         super.onDispose();
      }

      internal function frame1() : *
      {
         stop();
      }
      
      internal function frame2() : *
      {
         stop();
      }
      
      internal function frame3() : *
      {
         stop();
      }
      
      internal function frame4() : *
      {
         stop();
      }
      
      internal function frame5() : *
      {
         stop();
      }
      
      internal function frame6() : *
      {
         stop();
      }
      
      internal function frame7() : *
      {
         stop();
      }
   }
}

