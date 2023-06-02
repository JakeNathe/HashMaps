# Name: Jake Nathe
# OSU Email: nathej@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: 6
# Due Date: 6/12/2023
# Description: A hash map ADT that uses open addressing for collisions.

from a6_include import (DynamicArray, DynamicArrayException, HashEntry,
                        hash_function_1, hash_function_2)


class HashMap:
    def __init__(self, capacity: int, function) -> None:
        """
        Initialize new HashMap that uses
        quadratic probing for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(None)

        self._hash_function = function
        self._size = 0

    def __str__(self) -> str:
        """
        Override string method to provide more readable output
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        out = ''
        for i in range(self._buckets.length()):
            out += str(i) + ': ' + str(self._buckets[i]) + '\n'
        return out

    def _next_prime(self, capacity: int) -> int:
        """
        Increment from given number to find the closest prime number
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity % 2 == 0:
            capacity += 1

        while not self._is_prime(capacity):
            capacity += 2

        return capacity

    @staticmethod
    def _is_prime(capacity: int) -> bool:
        """
        Determine if given integer is a prime number and return boolean
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity == 2 or capacity == 3:
            return True

        if capacity == 1 or capacity % 2 == 0:
            return False

        factor = 3
        while factor ** 2 <= capacity:
            if capacity % factor == 0:
                return False
            factor += 2

        return True

    def get_size(self) -> int:
        """
        Return size of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._size

    def get_capacity(self) -> int:
        """
        Return capacity of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._capacity

    # ------------------------------------------------------------------ #

    def _get_hash_key (self, key: str, capacity: int) -> int:
        """Helper function to calculate the hash key with quadratic probing."""
        hash_key = self._hash_function(key)
        hash_key %= capacity
        hash_const = hash_key
        q_probing = 1

        if self._buckets[hash_key] is None or self._buckets[hash_key].is_tombstone is True:
            return hash_key

        while self._buckets[hash_key] is not None:
            # return if key matches to replace value
            if self._buckets[hash_key].key == key:
                return hash_key
            # update based on quadratic probing
            hash_key = (hash_const + q_probing ** 2) % capacity
            q_probing += 1

        return hash_key

    def put(self, key: str, value: object) -> None:
        """
        Adds the key:value pair to the hash map. Resizes if needed.
        """
        # check if resize is needed
        if self.table_load() >= 0.5:
            self.resize_table(self._capacity * 2)

        new_obj = HashEntry(key, value)
        hash_key = self._get_hash_key(key, self._capacity)
        index = self._buckets[hash_key]

        # replace value if key already exists
        if index is not None:
            if index.key == key:
                index.value = value
                return

        self._buckets[hash_key] = new_obj
        self._size += 1

    def table_load(self) -> float:
        """
        Returns the current table load factor
        """
        return self._size / self._capacity

    def empty_buckets(self) -> int:
        """
        Returns the amount of empty buckets in the hash table
        """
        empty_buckets = 0
        for index in range(self._buckets.length()):
            if self._buckets[index] is None or self._buckets[index].is_tombstone:
                empty_buckets += 1

        return empty_buckets

    def resize_table(self, new_capacity: int) -> None:
        """
        Resizes the hash table and rehashes all existing keyss.
        """
        if self._size > new_capacity:
            return
        # capacity must be a prime number
        if self._is_prime(new_capacity) is False:
            new_capacity = self._next_prime(new_capacity)

        # new hash map with new capacity
        updated_map = HashMap(new_capacity, self._hash_function)

        # iterate over the buckets of temp map and insert into the actual map
        for index in range(self._capacity):
            hash_obj = self._buckets[index]
            if hash_obj is not None and hash_obj.is_tombstone is False:
                updated_map.put(hash_obj.key, hash_obj.value)

        self._buckets = updated_map._buckets
        self._capacity = updated_map._capacity

    def get(self, key: str) -> object:
        """
        Checks if key is in hash map. If so, returns the value associated with the key
        """
        hash_key = self._get_hash_key(key, self._capacity)
        index = self._buckets[hash_key]

        if index is None or index.is_tombstone is True:
            return None
        elif index.key == key and index.is_tombstone is False:
            return index.value
        else:
            return None

    def contains_key(self, key: str) -> bool:
        """
        Checks if hash map contains the key, if so returns True.
        """
        hash_key = self._get_hash_key(key, self._capacity)
        index = self._buckets[hash_key]

        if index is None or index.is_tombstone is True:
            return False
        elif index.key == key and index.is_tombstone is False:
            return True
        else:
            return False

    def remove(self, key: str) -> None:
        """
        Removes the key from the hash map if it exists.
        """
        # find index the key would be at
        hash_key = self._get_hash_key(key, self._capacity)
        index = self._buckets[hash_key]

        if index is None or index.is_tombstone is True:
            return
        else:
            # replace with TS
            index.is_tombstone = True
            self._size -= 1
            return

    def clear(self) -> None:
        """
        Clears contents of the hash map. Capacity is not changed.
        """
        empty_buckets = DynamicArray()

        for _ in range(self._capacity):
            empty_buckets.append(None)

        self._buckets = empty_buckets
        self._size = 0

    def get_keys_and_values(self) -> DynamicArray:
        """
        Returns an array that list all key:value pairs stored in the has map as tuples.
        Array is unordered
        """
        result = DynamicArray()

        for num in range(self._capacity):
            index = self._buckets[num]
            if index is not None and index.is_tombstone is False:
                result.append((index.key, index.value))

        return result

    def __iter__(self):
        """
        Create iterator for loop
        """
        self._index = 0
        return self

    def __next__(self):
        """
        Obtain the next value and advance interator
        """
        try:
            value = self._buckets[self._index]
            while value is None:
                self._index += 1
                value = self._buckets[self._index]
        except DynamicArrayException:
            raise StopIteration

        self._index += 1
        return value


# ------------------- BASIC TESTING ---------------------------------------- #

if __name__ == "__main__":

    print("\nPDF - put example 1")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('str' + str(i), i * 100)
        if i % 25 == 24:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - put example 2")
    print("-------------------")
    m = HashMap(41, hash_function_2)
    for i in range(50):
        m.put('str' + str(i // 3), i * 100)
        if i % 10 == 9:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - table_load example 1")
    print("--------------------------")
    m = HashMap(101, hash_function_1)
    print(round(m.table_load(), 2))
    m.put('key1', 10)
    print(round(m.table_load(), 2))
    m.put('key2', 20)
    print(round(m.table_load(), 2))
    m.put('key1', 30)
    print(round(m.table_load(), 2))

    print("\nPDF - table_load example 2")
    print("--------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(50):
        m.put('key' + str(i), i * 100)
        if i % 10 == 0:
            print(round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 1")
    print("-----------------------------")
    m = HashMap(101, hash_function_1)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 30)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key4', 40)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 2")
    print("-----------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('key' + str(i), i * 100)
        if i % 30 == 0:
            print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - resize example 1")
    print("----------------------")
    m = HashMap(20, hash_function_1)
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))
    m.resize_table(30)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))

    print("\nPDF - resize example 2")
    print("----------------------")
    m = HashMap(75, hash_function_2)
    keys = [i for i in range(25, 1000, 13)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())

    for capacity in range(111, 1000, 117):
        m.resize_table(capacity)

        if m.table_load() > 0.5:
            print(f"Check that the load factor is acceptable after the call to resize_table().\n"
                  f"Your load factor is {round(m.table_load(), 2)} and should be less than or equal to 0.5")

        m.put('some key', 'some value')
        result = m.contains_key('some key')
        m.remove('some key')

        for key in keys:
            # all inserted keys must be present
            result &= m.contains_key(str(key))
            # NOT inserted keys must be absent
            result &= not m.contains_key(str(key + 1))
        print(capacity, result, m.get_size(), m.get_capacity(), round(m.table_load(), 2))

    print("\nPDF - get example 1")
    print("-------------------")
    m = HashMap(31, hash_function_1)
    print(m.get('key'))
    m.put('key1', 10)
    print(m.get('key1'))

    print("\nPDF - get example 2")
    print("-------------------")
    m = HashMap(151, hash_function_2)
    for i in range(200, 300, 7):
        m.put(str(i), i * 10)
    print(m.get_size(), m.get_capacity())
    for i in range(200, 300, 21):
        print(i, m.get(str(i)), m.get(str(i)) == i * 10)
        print(i + 1, m.get(str(i + 1)), m.get(str(i + 1)) == (i + 1) * 10)

    print("\nPDF - contains_key example 1")
    print("----------------------------")
    m = HashMap(11, hash_function_1)
    print(m.contains_key('key1'))
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key3', 30)
    print(m.contains_key('key1'))
    print(m.contains_key('key4'))
    print(m.contains_key('key2'))
    print(m.contains_key('key3'))
    m.remove('key3')
    print(m.contains_key('key3'))

    print("\nPDF - contains_key example 2")
    print("----------------------------")
    m = HashMap(79, hash_function_2)
    keys = [i for i in range(1, 1000, 20)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())
    result = True
    for key in keys:
        # all inserted keys must be present
        result &= m.contains_key(str(key))
        # NOT inserted keys must be absent
        result &= not m.contains_key(str(key + 1))
    print(result)

    print("\nPDF - remove example 1")
    print("----------------------")
    m = HashMap(53, hash_function_1)
    print(m.get('key1'))
    m.put('key1', 10)
    print(m.get('key1'))
    m.remove('key1')
    print(m.get('key1'))
    m.remove('key4')

    print("\nPDF - clear example 1")
    print("---------------------")
    m = HashMap(101, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key1', 30)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - clear example 2")
    print("---------------------")
    m = HashMap(53, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.get_size(), m.get_capacity())
    m.resize_table(100)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - get_keys_and_values example 1")
    print("------------------------")
    m = HashMap(11, hash_function_2)
    for i in range(1, 6):
        m.put(str(i), str(i * 10))
    print(m.get_keys_and_values())

    m.resize_table(2)
    print(m.get_keys_and_values())

    m.put('20', '200')
    m.remove('1')
    m.resize_table(12)
    print(m.get_keys_and_values())

    print("\nPDF - __iter__(), __next__() example 1")
    print("---------------------")
    m = HashMap(10, hash_function_1)
    for i in range(5):
        m.put(str(i), str(i * 10))
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)

    print("\nPDF - __iter__(), __next__() example 2")
    print("---------------------")
    m = HashMap(10, hash_function_2)
    for i in range(5):
        m.put(str(i), str(i * 24))
    m.remove('0')
    m.remove('4')
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)
