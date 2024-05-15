import os
import streamlit as st
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Stop Words From file
Stop_words_list = [
    'a', 'is', 'the', 'of', 'all', 'and', 'to', 'can', 'be', 'as', 'once', 'for', 'at', 'am', 'are', 'has', 'have', 'had', 'up', 'his', 'her', 'in', 'on', 'no', 'we', 'do'
]

porter_stemmer = PorterStemmer()

#This function tokenizes the text and removes stop words from it and perform stemming using porter stemmer.
def Pre_Processing(text):
    # Tokenization
    tokens = word_tokenize(text)

    # Filtering tokens by removing URLS,numbers,stopwords and converting to lowercase.
    filtered_tokens = []
    for token in tokens:
        if not token.startswith("http://") and not token.startswith("https://"):
            if not any(char.isdigit() for char in token):
                lower_token = token.lower()
                if lower_token not in Stop_words_list:
                    filtered_tokens.append(lower_token)

    # Performed stemming on Filtered tokens.
    stemmed_tokens = []
    for token in filtered_tokens:
        stemmed_token = porter_stemmer.stem(token)
        stemmed_tokens.append(stemmed_token)

    return stemmed_tokens

#Creation of Inverted Index by iterating over each file in the directory, reads its content, and preprocesses the text to extract terms,The terms extracted are added to the inverted index along with their corresponding document IDs and positions.
def Inverted_idx(directory):
    inverted_index = {}
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), "r") as file:
            text = file.read()
            terms = Pre_Processing(text)
            doc_id = filename
            for position, term in enumerate(terms):
                if term not in inverted_index:
                    inverted_index[term] = {}
                if doc_id not in inverted_index[term]:
                    inverted_index[term][doc_id] = []
                inverted_index[term][doc_id].append(position)
    return inverted_index

#This function processes a Boolean query using the inverted index and returns a set of document IDs that satisfy the Boolean query.
def Boolean_Query_Processing(inverted_index, query_terms, operators):
    if not operators:
        return set(get_documents(inverted_index, query_terms[0]))

    result = set(get_documents(inverted_index, query_terms[0]))

    i = 1
    while i < len(query_terms):
        term = query_terms[i]
        operator = operators[i - 1]

        if operator == 'AND':
            result = result.intersection(get_documents(inverted_index, term))
        elif operator == 'OR':
            result = result.union(get_documents(inverted_index, term))
        elif operator == 'NOT':
            result = result.difference(get_documents(inverted_index, term))

        i += 1

    return result

#This function processes a proximity query on an inverted index to find documents where two terms appear within a specified distance of each other.
def Proximity_Query_Processing(inverted_index, term1, term2, k):
    if term1 not in inverted_index or term2 not in inverted_index:
        return []

    result = set()
    posting_list_1 = inverted_index[term1]
    posting_list_2 = inverted_index[term2]

    common_docs = set(posting_list_1.keys()) & set(posting_list_2.keys())

    for doc_id in common_docs:
        positions1 = posting_list_1[doc_id]
        positions2 = posting_list_2[doc_id]

        for pos1 in positions1:
            for pos2 in positions2:
                if abs(pos1 - pos2) <= k:
                    result.add(doc_id)
                    break
    return result

#This function retrieves the set of documents containing a given term from the inverted index.
def get_documents(inverted_index, term):
    return inverted_index.get(term, set())

#This function Split the query into terms and operators
def parse_query(query):
    terms = query.split()
    operators = []
    query_terms = []
    for term in terms:
        if term.upper() in ['AND', 'OR', 'NOT']:
            operators.append(term.upper())
        else:
            stemmed_term = porter_stemmer.stem(term.lower())
            query_terms.append(stemmed_term)
    return query_terms, operators

#Main Function. Loads inverted index and calls GUI function.
def main():
    st.title("Boolean Retrieval Model by Usman Arif")
    query_type = st.radio("Select query type:", ("Boolean", "Proximity"))
    directory = st.text_input("Enter directory path containing research papers:", value=r"C:\Users\uarif\OneDrive\Documents\Semester 6\Information Retrieval\Assignment 01\ResearchPapers\ResearchPapers")
    inverted_index = Inverted_idx(directory)

    if query_type == "Boolean":
        query = st.text_input("Enter your boolean query (e.g., 'term1 AND term2 OR term3 NOT term4'):")
    else:
        query = st.text_input("Enter your proximity query (e.g., 'term1 term2'):")

    if query_type == "Proximity":
        k = st.number_input("Enter the value of K (for Proximity Query):", value=1)

    if st.button("Perform Query"):
        if query_type == "Boolean":
            query_terms, operators = parse_query(query)
            result = Boolean_Query_Processing(inverted_index, query_terms, operators)
        else:
            preprocessed_query = Pre_Processing(query)
            term1 = preprocessed_query[0]
            term2 = preprocessed_query[1]
            result = Proximity_Query_Processing(inverted_index, term1, term2, k)
        if result:
            formatted_result = [os.path.splitext(doc_id)[0] for doc_id in result]
            st.write("Documents found:", ', '.join(formatted_result))
        else:
            st.write("No documents found matching the query.")

if __name__ == "__main__":
    main()
