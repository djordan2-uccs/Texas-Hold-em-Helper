import java.io.IOException;
import java.util.Scanner;
import java.io.FileWriter;
import java.io.PrintWriter;

public class cardReader {

	public static void main(String[] args) throws IOException {
		
		String fileName = "cards.txt";
		
		Scanner input = new Scanner(System.in);
		
		int phase = 1;
		
		// Gather the current phase of the game from the user.
	    // Also gather 7 cards from the user's input.
		
		System.out.println("Input the phase of the game. ('1' indicates only the flop is visible, '2' indicates the turn is visible, and '3' indicates all cards are visible.");
		
		phase = input.nextInt();
		
		// If the phase is out of range, say as such and reprompt the user.
		while (phase < 0 && phase >3) {
			
			System.out.println("Phase number is out of range. Please re-input.");
			
			phase = input.nextInt();
			
		}
		
	    System.out.println("Input a string of " + (4 + phase) + " cards. \nYour first 2 will represent your hole, the next 3 will be the flop, and the last 2 are the turn and river depending on the phase..");
		
		Card[] cardArray = getCards(input, phase);
		
		// If the card string was invalid, say as such and reprompt the user.
		while (cardArray == null) {
			
			System.out.println("There was an error processing your cards. Please try again.");
			
			cardArray = getCards(input, phase);
			
		}
		
			
		try (PrintWriter writer = new PrintWriter(new FileWriter(fileName))){
				
			for (int i = 0; i < 4 + phase; i++) {
				
				writer.print(cardArray[i].printCard() + " ");
				
			}
		}
			
		catch (IOException e){
				
			System.out.println("There was an error trying to write to the file.");
				
		}
		
		input.close();

	}
	
	// Gets the cards needed to perform evaluations.
	public static Card[] getCards(Scanner input, int phase) {

	    // This will store the valid, non-duplicate cards
	    Card[] cardArray = new Card[4 + phase]; 

	    // Break each segment of the input up.
	    for (int i = 0; i < (4 + phase); i++) {

	        // Take 1 segment...
	        String cardString = input.next();

	        try {
	            // Assign the character from the beginning to suit.
	            char suit = cardString.charAt(0);

	            // Then, take the number at the end of a segment...
	            String numString = cardString.substring(1);

	            // And assign it to value.
	            int value = Integer.parseInt(numString);

	            // Create the new card object.
	            Card newCard = new Card(suit, value);

	            // Check for duplicates.
	            for (int j = 0; j < i; j++) {
	            	
	            	// If there is a duplicate card...
	                if (newCard.equals(cardArray[j])) {
	                	
	                	// Clear the input line...
	    	            if (input.hasNextLine()) {
	    	            	
	    	            	input.nextLine();
	    	            	
	    	            }
	    	            
	    	            // ...tell the user as such, and return null.
	    	            System.out.println("Duplicate Card: " + cardString);
	                    
	                    return null;
	                }
	            }
	            
	            // If no duplicate is found, add the new card to the set.
	            cardArray[i] = newCard;

	        } 
	        
	        // Catch any invalid strings.
	        catch (NumberFormatException | StringIndexOutOfBoundsException e) {
	       
	            // Handle invalid card format...
	            System.out.println("Invalid Card String Format: " + cardString);
	            
	            // Clear the input line, and return null.
	            if (input.hasNextLine()) {
	            	
	            	input.nextLine();
	            	
	            }
	            
	            return null;
	        }
	    }

	    // If everything runs smoothly, return the set of cards.

	    return cardArray;
	}
}
