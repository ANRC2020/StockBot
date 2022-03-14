#include <iostream>
#include <vector>
using namespace std;

struct Link {
    int val = 0;
    Link* next = nullptr;

    Link(){
        val = 0;
        next = nullptr;
    }

    Link(int x){
        val = x;
    }

};

Link* makeLinkedList(vector<int> vec){
    int size = vec.size();
    Link* ptr;
    Link* prev;
    Link* head;

    for(int i = 0; i < size; i++){
        Link *node = new Link(vec.at(i));
        ptr = node;

        if(i == 0){
            head = ptr;
            prev = ptr;
        } else {
            prev->next = ptr;
            prev = ptr;
        }
    }

    return head;
}

int main() {
    int size = 0;
    
    cout << "How many links? " << endl;
    cin >> size;

    vector<int> arr = {};
    int temp = 0;

    for(int i = 0; i < size; i++) {
        cout << "Enter a number: ";
        cin >> temp;
        cout << "\n";        
        arr.push_back(temp);
    }

    Link* head = makeLinkedList(arr);
    Link* temp = head;

    for(int i = 0; i < size; i++) {
        cout << temp << " ";  
    }

}