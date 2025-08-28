import socket

def node_vote_server(node_id, decision=True):
    s = socket.socket()
    s.bind(("localhost", 9000 + node_id))
    s.listen(1)
    while True:
        conn, _ = conn.accept()
        conn.send(b"1" if decision else b"0")
        conn.close()

def swarm_vote(patch_id, node_ids):
    votes = {}
    for nid in node_ids:
        try:
            s = socket.socket()
            s.connect(("localhost", 9000 + nid))
            vote = s.recv(1)
            votes[f"node{nid}"] = vote == b"1"
            s.close()
        except:
            votes[f"node{nid}"] = False
    approved = sum(votes.values()) > len(votes) // 2
    return {"votes": votes, "approved": approved}

