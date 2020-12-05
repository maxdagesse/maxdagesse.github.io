#include <algorithm>
#include <climits>
#include <iostream>
#include <string> // atoi
#include <time.h>

#include "CSVparser.hpp"

using namespace std;

// Global definitions visible to all methods and classes

const unsigned int DEFAULT_SIZE = 179;

// forward declarations
double strToDouble(string str, char ch);

// define a structure to hold bid information
struct Bid {
    string bidId; // unique identifier
    string title;
    string fund;
    double amount;
    Bid() {
        amount = 0.0;
    }
};

// Hash Table class definition
class HashTable {

private:
    // defines structure to hold bids
	struct Node {
		Bid _bid;
		unsigned _key;
		Node* next;

    //initializer
		Node() {
			_key = UINT_MAX;
			next = nullptr;
		}

		//initializer with a bid
		Node(Bid bid) : Node() {
			_bid = bid;
		}

		//initializer with a bid and key
		Node(unsigned key, Bid bid) : Node() {
			_bid = bid;
			_key = key;
		}



	};

	vector<Node> nodes;

	unsigned hashTblSize = 550;


    unsigned int hash(int key);

public:
    HashTable();
    virtual ~HashTable();
    void Insert(Bid bid);
    void PrintAll();
    void Remove(string bidId);
    Bid Search(string bidId);
    Bid SearchByTitle(string title);
};

// Default constructor
HashTable::HashTable() {
    // initializes the structures used to hold bids
	nodes.resize(hashTblSize);
}
// Destructor
HashTable::~HashTable() {
    // logic to free storage when class is destroyed
	nodes.erase(nodes.begin());
}

/**
 * Calculate the hash value of a given key.
 * Note that key is specifically defined as
 * unsigned int to prevent undefined results
 * of a negative list index.
 */
unsigned int HashTable::hash(int key) {
    //logic to calculate a hash value
	return key % hashTblSize;
}

//Insert a bid
void HashTable::Insert(Bid bid) {
    // logic to insert a bid
	int key = hash(atoi(bid.bidId.c_str()));

	// Get the node using key
	Node* oldNode = &(nodes.at(key));

	if(oldNode != nullptr) {
		// Node found
		if (oldNode->_key == UINT_MAX) {
			oldNode->_key = key;
			oldNode->_bid = bid;
			oldNode->next = nullptr;
		} else {
			// Do the hash chaining
			while(true) {
				if(oldNode->next == nullptr) {
					break;
				}
				oldNode = oldNode->next;
			}
			oldNode->next = new Node(key, bid);
		}

	} else {
		Node* newNode = new Node(key,bid);
		nodes.insert(nodes.begin() + key, *newNode);
	}
}

//Print all bids
void HashTable::PrintAll() {
    // logic to print all bids
	for (auto nodeSearch = nodes.begin(); nodeSearch != nodes.end(); ++nodeSearch) {
	//Set the conditional if not UINT_MAX and output the key and bid data:
		if (nodeSearch->_key != UINT_MAX) {
			cout << "#" << nodeSearch->_key << " | " << nodeSearch->_bid.bidId << ": " << nodeSearch->_bid.title << " | " << nodeSearch->_bid.amount << " | " << nodeSearch->_bid.fund << endl;
	    //While node not equal to nullptr, output the node data
			Node* node = nodeSearch->next;
			while (node != nullptr) {
				cout << "    " << node->_key << ": " << node->_bid.bidId << " | " << node->_bid.title << " | " << node->_bid.amount << " | " << node->_bid.fund << endl;
			node = node->next;
			}
		}
	}
}

//Remove a bid
void HashTable::Remove(string bidId) {
    // logic to remove a bid
	int keyToRemove = hash(atoi(bidId.c_str()));
	nodes.erase(nodes.begin() + keyToRemove);
}

//Search for the specified bidId
Bid HashTable::Search(string bidId) {
    // logic to search for and return a bid
    Bid bid;
    int key = hash(atoi(bidId.c_str()));
    Node* node = &(nodes.at(key));
    // If the node which matches the key is found
    bool nodeExist = node != nullptr;
    // If no node exists (fail fast condition)
    if(!nodeExist || node->_key == UINT_MAX) {
    	return bid;
    }
    bool keyNotMax = node->_key != UINT_MAX;
    bool isSameAsNodeBeingSearched = node->_bid.bidId.compare(bidId) == 0;
    if (nodeExist && keyNotMax && isSameAsNodeBeingSearched) {
    	return node->_bid;
    }
    while(true) {
    	if (node == nullptr) {
    		break;
    	}
    	if (keyNotMax && node->_bid.bidId.compare(bidId) == 0) {
    		return node->_bid;
    	}
    	node = node->next;
    }
    return bid;
}

//Display the bid information to the console
void displayBid(Bid bid) {
    cout << bid.bidId << ": " << bid.title << " | " << bid.amount << " | "
            << bid.fund << endl;
    return;
}

//Load a CSV file containing bids into a container
void loadBids(string csvPath, HashTable* hashTable) {
    cout << "Loading CSV file " << csvPath << endl;

    // initialize the CSV Parser using the given path
    csv::Parser file = csv::Parser(csvPath);
    try {
        // loop to read rows of a CSV file
        for (unsigned int i = 0; i < file.rowCount(); i++) {

            // Create a data structure and add to the collection of bids
            Bid bid;
            bid.bidId = file[i][1];
            bid.title = file[i][0];
            bid.fund = file[i][8];
            bid.amount = strToDouble(file[i][4], '$');

            // push this bid to the end
            hashTable->Insert(bid);
        }
    } catch (csv::Error &e) {
        std::cerr << e.what() << std::endl;
    }
}

//Convert a string to a double after stripping out unwanted char
double strToDouble(string str, char ch) {
    str.erase(remove(str.begin(), str.end(), ch), str.end());
    return atof(str.c_str());
}

int main(int argc, char* argv[]) {

    // process command line arguments
    string csvPath, bidKey;
    switch (argc) {
    case 2:
        csvPath = argv[1];
        bidKey = "98109";
        break;
    case 3:
        csvPath = argv[1];
        bidKey = argv[2];
        break;
    default:
        csvPath = "eBid_Monthly_Sales_Dec_2016.csv";
        bidKey = "98109";
    }

    // Define a timer variable
    clock_t ticks;

    // Define a hash table to hold all the bids
    HashTable* bidTable;

    Bid bid;

    int choice = 0;
    int choiceTwo = 0;
    while (choice != 9) {
        cout << "Menu:" << endl;
        cout << "  1. Load Bids from CSV File" << endl;
        cout << "  2. Display All Bids" << endl;
        cout << "  3. Find Bid by ID" << endl;
        cout << "  4. Remove Bid by ID" << endl;
        cout << "  9. Exit" << endl;
        cout << "Enter choice: ";
        cin >> choice;

        switch (choice) {

        case 1:
            bidTable = new HashTable();

            cout << "Which CSV file would you like to load?" << endl;
            cout << "  1. eBid_Monthly_Sales_Dec_2016.csv" << endl;
            cout << "  2. eBid_Monthly_Sales.csv" << endl;
            cout << "  3. Input your own file name." << endl;
            cin >> choiceTwo;

            if (choiceTwo == 1) {
              csvPath = "eBid_Monthly_Sales_Dec_2016.csv";
            }
            else if (choiceTwo == 2) {
              csvPath = "eBid_Monthly_Sales.csv";
            }
            else if (choiceTwo == 3) {
              cout << "Input file name: " << endl;
              cin >> csvPath;
            }
            else {
              cout << "Invalid argument; defaulting to eBid_Monthly_Sales_Dec_2016.csv" << endl;
              csvPath = "eBid_Monthly_Sales_Dec_2016.csv";
            }

            // Initialize a timer variable before loading bids
            ticks = clock();

            // Complete the method call to load the bids
            loadBids(csvPath, bidTable);

            // Calculate elapsed time and display result
            ticks = clock() - ticks; // current clock ticks minus starting clock ticks
            cout << "time: " << ticks << " clock ticks" << endl;
            cout << "time: " << ticks * 1.0 / CLOCKS_PER_SEC << " seconds" << endl;
            break;

        case 2:
            bidTable->PrintAll();
            break;

        case 3:
            ticks = clock();

            cout << "Enter bid ID to search: ";
            cin >> bidKey;

            bid = bidTable->Search(bidKey);

            ticks = clock() - ticks; // current clock ticks minus starting clock ticks

            if (!bid.bidId.empty()) {
                displayBid(bid);
            } else {
                cout << "Bid ID " << bidKey << " not found." << endl;
            }

            cout << "time: " << ticks << " clock ticks" << endl;
            cout << "time: " << ticks * 1.0 / CLOCKS_PER_SEC << " seconds" << endl;
            break;

        case 4:

            cout << "Enter bid ID to remove: ";
            cin >> bidKey;

            bidTable->Remove(bidKey);
            break;
        }
    }

    cout << "Good bye." << endl;

    return 0;
}