import javax.swing.*;
import java.awt.*;
import java.io.*;

public class CardReader extends JFrame {

    // Labels shown to user in dropdown
    private static final String[] RANK_LABELS = {
            "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"
    };

    // Actual values to pass to Card constructor (1-13)
    // 1 = Two, 2 = Three, ..., 12 = King, 13 = Ace (matches Python)
    private static final int[] RANK_VALUES = {
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
    };

    private static final String[] SUIT_LABELS = {
            "♣ Clubs", "♦ Diamonds", "♠ Spades", "♥ Hearts"
    };

    private static final char[] SUIT_CHARS = {
            'c', 'd', 's', 'h'
    };

    private JComboBox<String> phaseBox;
    private JPanel centerPanel;
    private JComboBox<String>[] rankBoxes;
    private JComboBox<String>[] suitBoxes;

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            CardReader gui = new CardReader();
            gui.setVisible(true);
        });
    }

    public CardReader() {
        setTitle("Poker Card Input");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout(8, 8));

        JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 8));
        top.add(new JLabel("Select phase: "));
        phaseBox = new JComboBox<>(new String[]{"1", "2", "3"});
        phaseBox.addActionListener(e -> rebuildCardInputs());
        top.add(phaseBox);
        add(top, BorderLayout.NORTH);

        rebuildCardInputs();

        JPanel bottom = new JPanel(new FlowLayout(FlowLayout.CENTER, 8, 8));
        JButton runBtn = new JButton("Run Analyzer");
        runBtn.addActionListener(e -> runAnalyzer());
        bottom.add(runBtn);
        add(bottom, BorderLayout.SOUTH);

        pack();
        setLocationRelativeTo(null);
    }

    private void rebuildCardInputs() {
        if (centerPanel != null) remove(centerPanel);

        int phase = Integer.parseInt((String) phaseBox.getSelectedItem());
        int cardCount = 4 + phase;

        centerPanel = new JPanel(new GridLayout(cardCount, 1, 6, 6));

        rankBoxes = new JComboBox[cardCount];
        suitBoxes = new JComboBox[cardCount];

        for (int i = 0; i < cardCount; i++) {
            JPanel row = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 4));
            
            // Label based on position
            if (i < 2) {
                row.add(new JLabel("Hole Card " + (i + 1) + ":"));
            } else {
                row.add(new JLabel("Board Card " + (i - 1) + ":"));
            }

            rankBoxes[i] = new JComboBox<>(RANK_LABELS);
            suitBoxes[i] = new JComboBox<>(SUIT_LABELS);

            row.add(rankBoxes[i]);
            row.add(suitBoxes[i]);

            centerPanel.add(row);
        }

        add(centerPanel, BorderLayout.CENTER);
        revalidate();
        repaint();
        pack();
    }

    private void runAnalyzer() {
        int phase = Integer.parseInt((String) phaseBox.getSelectedItem());
        int cardCount = 4 + phase;

        Card[] cards = new Card[cardCount];

        // Build card objects & check duplicates
        for (int i = 0; i < cardCount; i++) {
            int rIndex = rankBoxes[i].getSelectedIndex();
            int sIndex = suitBoxes[i].getSelectedIndex();

            // Create card with value 1-13 (1=Two, 13=Ace)
            Card card = new Card(
                    SUIT_CHARS[sIndex],
                    RANK_VALUES[rIndex]
            );

            // Duplicate check
            for (int j = 0; j < i; j++) {
                if (card.equals(cards[j])) {
                    JOptionPane.showMessageDialog(this,
                            "Duplicate card selected at position " + (i + 1),
                            "Duplicate Card", JOptionPane.WARNING_MESSAGE);
                    return;
                }
            }

            cards[i] = card;
        }

        // Write cards.txt in Python format (e.g., "c1 h13 d5 s12 c3")
        File outFile = new File("cards.txt");
        try (PrintWriter writer = new PrintWriter(new FileWriter(outFile))) {
            for (Card c : cards) {
                writer.print(c.printCard() + " ");
            }
        } catch (IOException e) {
            JOptionPane.showMessageDialog(this,
                    "Error writing cards.txt:\n" + e.getMessage(),
                    "File Error", JOptionPane.ERROR_MESSAGE);
            return;
        }

        // Run Python analyzer
        try {
            ProcessBuilder pb = new ProcessBuilder("python", "PokerAnalyzer.py");
            pb.redirectErrorStream(true);

            Process process = pb.start();
            BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream())
            );

            StringBuilder output = new StringBuilder();
            String line;

            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }

            process.waitFor();

            JTextArea textArea = new JTextArea(output.toString());
            textArea.setEditable(false);
            textArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
            JScrollPane scroll = new JScrollPane(textArea);
            scroll.setPreferredSize(new Dimension(600, 400));

            JOptionPane.showMessageDialog(this,
                    scroll,
                    "Analyzer Output",
                    JOptionPane.INFORMATION_MESSAGE);

        } catch (Exception e) {
            JOptionPane.showMessageDialog(this,
                    "Failed to run analyzer:\n" + e.getMessage(),
                    "Execution Error", JOptionPane.ERROR_MESSAGE);
        }
    }
}