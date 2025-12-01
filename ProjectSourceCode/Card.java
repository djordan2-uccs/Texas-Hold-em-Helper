//Class Card.
public class Card {
	
	// 'suit' represents the suit of the card (c, d, s, h)
	char suit;
	
	// 'value' represents the rank of the card (1-13)
	// 1 = Two, 2 = Three, ..., 12 = King, 13 = Ace
	int value;
	
	// Value names for display (indices 0-12 map to values 1-13)
	String[] valueNames = {"Two", "Three", "Four", "Five", "Six", "Seven", 
	                       "Eight", "Nine", "Ten", "Jack", "Queen", "King", "Ace"};
	
	String[] suitNames = {"Clubs", "Diamonds", "Spades", "Hearts"};
	
	// Constructor takes a suit (c/d/s/h) and a value (1-13)
	// Where 1=Two, 2=Three, ..., 12=King, 13=Ace
	public Card(char suit, int value) {
		// Validate and set suit
		if (suit == 'c' || suit == 'd' || suit == 's' || suit == 'h') {
			this.suit = suit;
		}
		
		// Validate and set value (1-13)
		if (value >= 1 && value <= 13) {
			this.value = value;
		}
	}
	
	public char getSuit() {
		return suit;
	}
	
	public int getValue() {
		return value;
	}
	
	public void setSuit(char suit) {
		this.suit = suit;
	}
	
	public void setValue(int value) {
		this.value = value;
	}
	
	// Returns card in format for Python (e.g., "c1", "h13")
	public String printCard() {
		int suitNumber = 0;
		
		switch (suit) {
			case 'c' -> suitNumber = 0;
			case 'd' -> suitNumber = 1;
			case 's' -> suitNumber = 2;
			case 'h' -> suitNumber = 3;
		}
		
		// Print format
		System.out.println(valueNames[value - 1] + " of " + suitNames[suitNumber]);
		
		// Return Python format: suit + value (e.g., "c1" for Two of Clubs)
		return String.valueOf(suit) + String.valueOf(value);
	}
	
	public boolean equals(Card card) {
		// Cards are equal if both suit and value match
		return this.suit == card.getSuit() && this.value == card.getValue();
	}
}