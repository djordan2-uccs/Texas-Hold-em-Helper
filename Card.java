//Class Card.
public class Card{
	
	// 'suit' represents the suit of the card.
	char suit;
	
	// 'value' represents the value of the card.
	int value;
	
	// 'valueNames' provide an easy way to convert values into names.
	String[] valueNames = {"Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King", "Ace"};
	
	String[] suitNames = {"Clubs", "Diamonds", "Spades", "Hearts"};
	
	// Constructor, takes a suit and a value.
	public Card (char suit, int value) {
		
		// If the suit is valid, set this suit to the given suit.
		if (suit == 'c' || suit == 'd' || suit == 's' || suit == 'h') {
			
			this.suit = suit;
			
		}
				
		if (value == 1) {
			
			this.value = 13;
		
		}
		
		else {
			
			this.value = value - 1;
			
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
	
	public String printCard() {
		
		int suitNumber = 0;
		
		switch (suit){
			
			case 'c':
				
				suitNumber = 0;
				
				break;
				
			case 'd':
				
				suitNumber = 1;
				
				break;
				
			case 's':
				
				suitNumber = 2;
				
				break;
				
			case 'h':
				
				suitNumber = 3;
				
				break;
				
		}
		
		System.out.println(valueNames[value - 1] + " of " + suitNames[suitNumber]);
		
		return String.valueOf(suit) + String.valueOf(value);
		
	}
	
	public boolean equals(Card card) {
		
		// If this card matches the incoming card, return true.
		if (this.suit == card.getSuit() && this.value == card.getValue()) {
			
			return true;
			
		}
		
		// Else, return false.
		else {
			
			return false;
			
		}
	}
}