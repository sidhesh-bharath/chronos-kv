Specification:

The Network & Protocol Layer:

Raw TCP sockets. Clients will connect via a TCP port and send commands terminated by a newline character (\n).

To keep authentication simple but fast, every command string sent by a client must start with the API key:
<api_key>:<command> <arguments>

Supported Commands:

AUTH <api_key> (Optional: validate connection upfront)
SET <key> <value> (Stores or updates a key)
GET <key> (Retrieves a value)
DEL <key> (Deletes a key)

The Storage Engine (In-Memory):
SET users:15 sidhesh -> db["users:15"] = "sidhesh"

The Append-Only Log (AOL) Format:

SET users:15 sidhesh
SET users:16 sanjeev
DEL users:15

When the server restarts, it reads database.log line by line and passes those lines straight into your execution function to perfectly rebuild the dictionary state.
