<?php
session_start();

class XiangqiGame {
    private $board;
    private $currentPlayer;
    private $gameOver;
    private $winner;
    
    public function __construct() {
        if (!isset($_SESSION['game'])) {
            $this->initGame();
        } else {
            $this->loadGame();
        }
    }
    
    private function initGame() {
        $this->board = $this->initBoard();
        $this->currentPlayer = 'red';
        $this->gameOver = false;
        $this->winner = null;
        $this->saveGame();
    }
    
    private function initBoard() {
        $board = array_fill(0, 10, array_fill(0, 9, null));
        
        // 黑方
        $board[0] = ['车','马','象','士','将','士','象','马','车'];
        $board[2][1] = '炮'; $board[2][7] = '炮';
        $board[3] = ['卒',null,'卒',null,'卒',null,'卒',null,'卒'];
        
        // 红方
        $board[9] = ['车','马','相','仕','帅','仕','相','马','车'];
        $board[7][1] = '炮'; $board[7][7] = '炮';
        $board[6] = ['兵',null,'兵',null,'兵',null,'兵',null,'兵'];
        
        return $board;
    }
    
    public function move($fromX, $fromY, $toX, $toY) {
        if ($this->gameOver) return false;
        
        $piece = $this->board[$fromY][$fromX];
        if (!$piece || $this->getPieceColor($piece) !== $this->currentPlayer) {
            return false;
        }
        
        if (!$this->isValidMove($fromX, $fromY, $toX, $toY)) {
            return false;
        }
        
        $this->board[$toY][$toX] = $piece;
        $this->board[$fromY][$fromX] = null;
        
        $this->checkGameOver();
        $this->currentPlayer = $this->currentPlayer === 'red' ? 'black' : 'red';
        $this->saveGame();
        
        return true;
    }
    
    private function isValidMove($fromX, $fromY, $toX, $toY) {
        if ($toX < 0 || $toX > 8 || $toY < 0 || $toY > 9) return false;
        
        $piece = $this->board[$fromY][$fromX];
        $target = $this->board[$toY][$toX];
        
        if ($target && $this->getPieceColor($target) === $this->getPieceColor($piece)) {
            return false;
        }
        
        $dx = abs($toX - $fromX);
        $dy = abs($toY - $fromY);
        
        switch ($piece) {
            case '车':
                return ($fromX === $toX || $fromY === $toY) && $this->isPathClear($fromX, $fromY, $toX, $toY);
            case '马':
                return (($dx === 2 && $dy === 1) || ($dx === 1 && $dy === 2)) && $this->checkHorseBlock($fromX, $fromY, $toX, $toY);
            case '象':
            case '相':
                return $dx === 2 && $dy === 2 && $this->checkElephantMove($fromX, $fromY, $toX, $toY);
            case '士':
            case '仕':
                return $dx === 1 && $dy === 1 && $this->checkAdvisorMove($fromX, $fromY, $toX, $toY);
            case '将':
            case '帅':
                return (($dx === 1 && $dy === 0) || ($dx === 0 && $dy === 1)) && $this->checkKingMove($fromX, $fromY, $toX, $toY);
            case '炮':
                return ($fromX === $toX || $fromY === $toY) && $this->checkCannonMove($fromX, $fromY, $toX, $toY);
            case '兵':
            case '卒':
                return $this->checkPawnMove($fromX, $fromY, $toX, $toY);
        }
        
        return false;
    }
    
    private function getPieceColor($piece) {
        return in_array($piece, ['车','马','象','士','将','炮','卒']) ? 'black' : 'red';
    }
    
    private function isPathClear($fromX, $fromY, $toX, $toY) {
        if ($fromX === $toX) {
            $start = min($fromY, $toY) + 1;
            $end = max($fromY, $toY);
            for ($y = $start; $y < $end; $y++) {
                if ($this->board[$y][$fromX]) return false;
            }
        } else {
            $start = min($fromX, $toX) + 1;
            $end = max($fromX, $toX);
            for ($x = $start; $x < $end; $x++) {
                if ($this->board[$fromY][$x]) return false;
            }
        }
        return true;
    }
    
    private function checkHorseBlock($fromX, $fromY, $toX, $toY) {
        $dx = $toX - $fromX;
        $dy = $toY - $fromY;
        
        if (abs($dx) === 2) {
            $blockX = $fromX + ($dx > 0 ? 1 : -1);
            return !$this->board[$fromY][$blockX];
        } else {
            $blockY = $fromY + ($dy > 0 ? 1 : -1);
            return !$this->board[$blockY][$fromX];
        }
    }
    
    private function checkElephantMove($fromX, $fromY, $toX, $toY) {
        $color = $this->getPieceColor($this->board[$fromY][$fromX]);
        if ($color === 'red' && $toY < 5) return false;
        if ($color === 'black' && $toY > 4) return false;
        
        $blockX = $fromX + ($toX > $fromX ? 1 : -1);
        $blockY = $fromY + ($toY > $fromY ? 1 : -1);
        return !$this->board[$blockY][$blockX];
    }
    
    private function checkAdvisorMove($fromX, $fromY, $toX, $toY) {
        if ($toX < 3 || $toX > 5) return false;
        $color = $this->getPieceColor($this->board[$fromY][$fromX]);
        if ($color === 'red' && ($toY < 7 || $toY > 9)) return false;
        if ($color === 'black' && ($toY < 0 || $toY > 2)) return false;
        return true;
    }
    
    private function checkKingMove($fromX, $fromY, $toX, $toY) {
        if ($toX < 3 || $toX > 5) return false;
        $color = $this->getPieceColor($this->board[$fromY][$fromX]);
        if ($color === 'red' && ($toY < 7 || $toY > 9)) return false;
        if ($color === 'black' && ($toY < 0 || $toY > 2)) return false;
        return true;
    }
    
    private function checkCannonMove($fromX, $fromY, $toX, $toY) {
        $target = $this->board[$toY][$toX];
        $piecesBetween = $this->countPiecesBetween($fromX, $fromY, $toX, $toY);
        
        if ($target) {
            return $piecesBetween === 1;
        } else {
            return $piecesBetween === 0;
        }
    }
    
    private function countPiecesBetween($fromX, $fromY, $toX, $toY) {
        $count = 0;
        if ($fromX === $toX) {
            $start = min($fromY, $toY) + 1;
            $end = max($fromY, $toY);
            for ($y = $start; $y < $end; $y++) {
                if ($this->board[$y][$fromX]) $count++;
            }
        } else {
            $start = min($fromX, $toX) + 1;
            $end = max($fromX, $toX);
            for ($x = $start; $x < $end; $x++) {
                if ($this->board[$fromY][$x]) $count++;
            }
        }
        return $count;
    }
    
    private function checkPawnMove($fromX, $fromY, $toX, $toY) {
        $color = $this->getPieceColor($this->board[$fromY][$fromX]);
        $dx = abs($toX - $fromX);
        $dy = $toY - $fromY;
        
        if ($color === 'red') {
            if ($fromY > 4) {
                return $dx === 0 && $dy === -1;
            } else {
                return ($dx === 0 && $dy === -1) || ($dx === 1 && $dy === 0);
            }
        } else {
            if ($fromY < 5) {
                return $dx === 0 && $dy === 1;
            } else {
                return ($dx === 0 && $dy === 1) || ($dx === 1 && $dy === 0);
            }
        }
    }
    
    private function checkGameOver() {
        $redKing = false;
        $blackKing = false;
        
        for ($y = 0; $y < 10; $y++) {
            for ($x = 0; $x < 9; $x++) {
                if ($this->board[$y][$x] === '帅') $redKing = true;
                if ($this->board[$y][$x] === '将') $blackKing = true;
            }
        }
        
        if (!$redKing) {
            $this->gameOver = true;
            $this->winner = 'black';
        } elseif (!$blackKing) {
            $this->gameOver = true;
            $this->winner = 'red';
        }
    }
    
    public function reset() {
        unset($_SESSION['game']);
        $this->initGame();
    }
    
    private function saveGame() {
        $_SESSION['game'] = [
            'board' => $this->board,
            'currentPlayer' => $this->currentPlayer,
            'gameOver' => $this->gameOver,
            'winner' => $this->winner
        ];
    }
    
    private function loadGame() {
        $game = $_SESSION['game'];
        $this->board = $game['board'];
        $this->currentPlayer = $game['currentPlayer'];
        $this->gameOver = $game['gameOver'];
        $this->winner = $game['winner'];
    }
    
    public function getBoard() { return $this->board; }
    public function getCurrentPlayer() { return $this->currentPlayer; }
    public function isGameOver() { return $this->gameOver; }
    public function getWinner() { return $this->winner; }
}

$game = new XiangqiGame();

if ($_POST['action'] ?? '' === 'move') {
    $game->move($_POST['fromX'], $_POST['fromY'], $_POST['toX'], $_POST['toY']);
    header('Content-Type: application/json');
    echo json_encode(['success' => true]);
    exit;
}

if ($_POST['action'] ?? '' === 'reset') {
    $game->reset();
    header('Location: index.php');
    exit;
}
?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>中国象棋</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background: #f0f0f0; }
        .board { margin: 20px auto; border: 3px solid #8B4513; background: #DEB887; }
        .cell { width: 60px; height: 60px; border: 1px solid #000; display: inline-block; 
                vertical-align: top; position: relative; cursor: pointer; }
        .piece { width: 50px; height: 50px; border-radius: 50%; margin: 5px; 
                 font-size: 18px; font-weight: bold; line-height: 50px; text-align: center; }
        .red { background: #fff; color: #f00; border: 2px solid #f00; }
        .black { background: #fff; color: #000; border: 2px solid #000; }
        .selected { box-shadow: 0 0 10px #ff0; }
        .river { background: #87CEEB; font-size: 14px; line-height: 60px; }
        .status { margin: 20px; font-size: 20px; font-weight: bold; }
        .controls { margin: 20px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>中国象棋</h1>
    
    <div class="status">
        <?php if ($game->isGameOver()): ?>
            游戏结束 - <?= $game->getWinner() === 'red' ? '红方' : '黑方' ?>胜利！
        <?php else: ?>
            当前轮到：<?= $game->getCurrentPlayer() === 'red' ? '红方' : '黑方' ?>
        <?php endif; ?>
    </div>
    
    <div class="board">
        <?php for ($y = 0; $y < 10; $y++): ?>
            <div>
                <?php for ($x = 0; $x < 9; $x++): ?>
                    <div class="cell <?= ($y === 4 || $y === 5) ? 'river' : '' ?>" 
                         onclick="cellClick(<?= $x ?>, <?= $y ?>)" id="cell-<?= $x ?>-<?= $y ?>">
                        <?php if ($y === 4): ?>
                            <?= $x < 4 ? '楚河' : ($x > 4 ? '汉界' : '') ?>
                        <?php endif; ?>
                        <?php if ($game->getBoard()[$y][$x]): ?>
                            <div class="piece <?= in_array($game->getBoard()[$y][$x], ['车','马','象','士','将','炮','卒']) ? 'black' : 'red' ?>" 
                                 id="piece-<?= $x ?>-<?= $y ?>">
                                <?= $game->getBoard()[$y][$x] ?>
                            </div>
                        <?php endif; ?>
                    </div>
                <?php endfor; ?>
            </div>
        <?php endfor; ?>
    </div>
    
    <div class="controls">
        <form method="post" style="display: inline;">
            <input type="hidden" name="action" value="reset">
            <button type="submit">重新开始</button>
        </form>
    </div>

    <script>
        let selectedCell = null;
        
        function cellClick(x, y) {
            if (<?= $game->isGameOver() ? 'true' : 'false' ?>) return;
            
            const cell = document.getElementById('cell-' + x + '-' + y);
            const piece = document.getElementById('piece-' + x + '-' + y);
            
            if (selectedCell) {
                // 尝试移动
                const fromX = selectedCell.x;
                const fromY = selectedCell.y;
                
                fetch('index.php', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: `action=move&fromX=${fromX}&fromY=${fromY}&toX=${x}&toY=${y}`
                }).then(() => {
                    location.reload();
                });
                
                // 清除选择
                document.getElementById('piece-' + selectedCell.x + '-' + selectedCell.y).classList.remove('selected');
                selectedCell = null;
            } else if (piece) {
                // 选择棋子
                const currentPlayer = '<?= $game->getCurrentPlayer() ?>';
                const pieceColor = piece.classList.contains('red') ? 'red' : 'black';
                
                if (pieceColor === currentPlayer) {
                    piece.classList.add('selected');
                    selectedCell = {x: x, y: y};
                }
            }
        }
    </script>
</body>
</html>