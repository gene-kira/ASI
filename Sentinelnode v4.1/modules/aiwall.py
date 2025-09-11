class ZeroTrustAIWall:
    def verify(self, actor):
        if actor in ["AI", "ASI", "unknown"]:
            print(f"[BLOCKED] Actor {actor} denied by ZeroTrustAIWall")
            return False
        return True

