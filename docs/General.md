# General

## Searching for qualified names

They store references by using a qualified name as a key in a dictionary:

```js
var vq = function(a, b, c) {
    ...
};
h["game.battle.controller.instant.BattleInstantPlay"] = vq;
```

So from here we see that `vq` is `game.battle.controller.instant.BattleInstantPlay`.
