package authenticationsystem;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Scanner;

public class AuthenticationSystem {
    public static void main(String[] args) throws Exception {
        Scanner scnr = new Scanner(System.in);//Scanner used for keyboard input.
        
        boolean loggingIn = false;//Tracks whether or not the user is attempting to log in.
      	boolean makingNewLogin = false;//Tracks whether or not the user is attempting to make a new login.
        boolean authSuccess = false;//This boolean is used to track whether authentication was successful.
        boolean credSecTest = false;//This will be used as part of a security test later.

        String username;//This string will store the username for whichever function the user opts into.
        String password;//This string will store the password for whichever function the user opts into.
        String passwordDigested;//This string will be used to store the MD5 digested password for new accounts made using the appropriate function.
        
        int counter = 0;//Tracks number of failed login attempts.
        
        File credFile = new File("credentials.txt");
        
        MD5Digest MD5 = new MD5Digest();//This initializes an object of the class I used to store the MD5 code for later.
        
        if(!credFile.exists()){
        //This checks to make sure the credentials file is present before anything else happens.
            System.out.println("The credentials file is inaccessible.\nThe system cannot be used.");
            //If it isn't present, the program exits.
        }
        else {
          System.out.println("Please enter the number of the option you wish to use:\n1: Log In To System\n2: Create New Account\nEnter anything else to exit program.");
          String userChoice = scnr.nextLine();
          if (userChoice.equals("1")) {
            loggingIn = true;
          }
          else if (userChoice.equals("2")) {
            makingNewLogin = true;
          }
        }

        while(loggingIn) {
            System.out.print("Enter user name: ");
            username = scnr.nextLine();//Accepts input for username
            System.out.print("Enter password: ");  
            password = scnr.nextLine();//Accepts input for password
            password = MD5.digest(password);
            //This runs the password through the MD5 code. The result immediately overwrites the original

            Scanner readCredFile = new Scanner(new FileInputStream(credFile));
            //This scanner is used to read from the credentials file.
            while(readCredFile.hasNextLine()){
            //This will continue looping until there are no more lines to read in the credentials file.
                String credentials[] = readCredFile.nextLine().split("\t");
                //This splits the current line being read in the credentials file into sections.
                //The split occurs at the tabs that seperate the username, password, and role.
                //The result is saved as a String for the program's use.
                if(credentials[0].trim().equals(username)) {
                //This checks if the input username matches the first section of the credentials.
                //That section is used to store the username.
                    if(credentials[1].trim().equals(password)) {
                    //This checks to see if the password matches the second section of the credentials line.
                    //That section is used to store the digested password.
                        authSuccess = true;
                        //If both of these are correct, the boolean used to track authentication success is set to "true".
                        File roleFile = new File(credentials[3].trim()+".txt");
                        //This creates a file reference for the program to use based on the split credentials line.
                        //The fourth section (index 3) has the role name saved, and the program reads this then appends the file extension.
                        boolean roleExists = roleFile.exists();
                        //This checks to see if the file for the role referenced exists. If not, it is set to false.
                            if(roleExists){
                            //If the role file exists, this code starts.
                                Scanner readRoleFile = new Scanner(new FileInputStream(roleFile));
                                //This scanner is used to read from the role file.
                                while(readRoleFile.hasNextLine()){
                                //This will loop until there are no more lines to read in the role file.
                                    System.out.println(readRoleFile.nextLine());
                                    //This prints the line that the program is currently on in the role file.
                                }
                            }
                            else {
                            //If the role file doesn't exist, this code starts in order to inform the user of the error.
                                System.out.println("It appears your role hasn't been added to our system yet.");
                            }
                            break;
                            }
                        }
                    }
                    if(authSuccess) {
                    //If the user was previously successful in logging in, this code starts.
                        System.out.println("Do you want to log out or exit the system?");
                        System.out.println("If you want to log out, enter \"logout\". If you want to exit the program, enter anything else: ");
                        //This takes the user's input on whether or not they wish to log out.
                        if(scnr.nextLine().toLowerCase().equals("logout")){
                        //If the above input is "logout", this code starts.
                            System.out.println("Logging out...");
                            authSuccess = false;
                            //This resets authSuccess, allowing the process to start from the beginning.
                            counter = 0;
                            //This resets the counter to 0 for future logins.
                        }
                        else{
                        //If the input is anything other than "logout", this code starts.
                            System.out.println("Have a good day.");
                            loggingIn = false;
                            //This sets the loop condition to false, ensuring that the loop will not continue.
                        }
                    }
                    else{
                        counter++;
                        //This increments the counter.
                        if(counter == 3){
                        //If the user has exceeded maximum attempts, this code starts.
                            System.out.println("Too many failed entries. Exiting...");
                            loggingIn = false;
                            //This sets the loop condition to false, ensuring that the loop will not continue.
                        }
                        else{
                            System.out.println("Incorrect credentials.");
                            System.out.println("Do you want to exit the system?");
                            System.out.println("If yes, enter \"exit\". If not, enter anything else: ");
                            //This takes the user's input on whether or not they wish to exit.
                            if(scnr.nextLine().toLowerCase().equals("exit")){
                            //If the above input is "exit", this code starts.
                                loggingIn = false;
                                //This sets the loop condition to false, ensuring that the loop will not continue.
                            }
                        }
                    }
        }
        while (makingNewLogin) {
          System.out.print("Enter new user's user name: ");
          username = scnr.nextLine();//Accepts input for username
          System.out.print("Enter new user's password: ");  
          password = scnr.nextLine();//Accepts input for password
          passwordDigested = MD5.digest(password);//This runs the password through the MD5 code and saves it as its own string.
          System.out.print("Enter new user's role: ");  
          String role = scnr.nextLine().toLowerCase();//Accepts input for role
          while (!credSecTest) {//This loop makes a security check related to the role of the user.
            if (role.equals("credentials")) {
              System.out.print("That role name is not allowed.\nEnter new user's role: ");  //If the new user's role is "credentials", this presents a security issue; logging in as that user will print the credentials file. This loop ensures that the user is not allowed to set their role as "credentials".
              role = scnr.nextLine().toLowerCase();//Accepts input for role
            }
            else {
              credSecTest = true;
            }
          }

          String newLogin = "\r" + username + "\t" + passwordDigested + "\t" + "\"" + password + "\"" + "\t" + role;//This assembles the components of the new account into a string that can be appended to the credentials file.

          FileOutputStream outputStream = new FileOutputStream(credFile, true);
          byte[] strToBytes = newLogin.getBytes();
          outputStream.write(strToBytes);//This section adds the new login info to the credentials file.

          System.out.println("Would you like to add another account to the system?");
          System.out.println("If you would, type \"yes\". If not, type anything else.");
          if(scnr.nextLine().toLowerCase().equals("yes")) {
            makingNewLogin = true;
          }
          else {
            makingNewLogin = false;
          }
        }
        System.out.println("Goodbye.");
    }
}