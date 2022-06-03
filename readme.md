# Summary
This script runs and plays a game of 1010.

---

## To do
1. Next move line clearance prediction
2. Max line clearance
3. min/max gaps and borders
4. evaluate gaps left across board
5. Combining shapes in hand

---
## Notes

### 03/06/21 - pt.2
The script now prioritises positions with the most bordering shapes/edges. Performance is roughly the same to fewest gaps. Need ot integrate a comparison between max borders and min gaps. Also need to consider the type of gaps left across the entire board after placing shape in proposed position and penalise smaller gaps.

### 03/06/21
Currently, the script places pieces in the position that results in the fewest gaps. This has resulted in fewer moves per game on average than the "first available position" strategy, but the playstyle is more strategic and with the addition of line clearance prediction, this should be improved. Additionally, the script needs to take into account the possibilities of combining the shapes in hand. For example, a 2x2 square and L shape can be combined into a 3x3 square

### 02/06/21
At this stage it will place a piece in the first available position on the board.