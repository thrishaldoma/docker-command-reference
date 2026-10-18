import http.client
import threading
import unittest
from server import Handler, LINES, ThreadingHTTPServer


class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path="/", ua="curl/8.0", method="GET"):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
        conn.request(method, path, headers={"User-Agent": ua})
        response = conn.getresponse()
        result = response.status, dict(response.getheaders()), response.read().decode()
        conn.close()
        return result

    def test_catalog_and_plain_text(self):
        status, headers, body = self.request()
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "text/plain; charset=utf-8")
        self.assertEqual(body.splitlines(), LINES)
        self.assertGreater(len(LINES), 200)
        self.assertEqual(len(LINES), len(set(line.split(" - ")[0] for line in LINES)))
        for line in LINES:
            self.assertRegex(line, r"^docker(?: [a-z0-9-]+)* - \S.+$")
        for command in ("docker run", "docker compose up", "docker buildx build",
                        "docker swarm init", "docker volume create", "docker config create",
                        "docker service scale", "docker node ls", "docker swarm leave",
                        "docker container list", "docker checkpoint create"):
            self.assertTrue(any(line.startswith(command + " - ") for line in LINES), command)
        self.assertFalse(any("init init" in line for line in LINES))

    def test_group_exact_command_and_search(self):
        status, _, body = self.request("/compose")
        self.assertEqual(status, 200)
        self.assertTrue(all(line.startswith("docker compose ") for line in body.splitlines()))
        status, _, body = self.request("/compose/up")
        self.assertEqual(status, 200)
        self.assertEqual(len(body.splitlines()), 1)
        self.assertTrue(body.startswith("docker compose up - "))
        status, _, body = self.request("/search?q=VOLUME")
        self.assertEqual(status, 200)
        self.assertTrue(all("volume" in line.lower() for line in body.splitlines()))

    def test_rejections_and_health(self):
        self.assertEqual(self.request(ua="Mozilla/5.0")[0], 403)
        self.assertEqual(self.request(ua="")[0], 403)
        self.assertEqual(self.request("/missing")[0], 404)
        self.assertEqual(self.request("/search?q=")[0], 400)
        self.assertEqual(self.request(method="POST")[0], 405)
        self.assertEqual(self.request("/healthz")[2], "ok\n")
        self.assertEqual(self.request(method="HEAD")[2], "")


if __name__ == "__main__":
    unittest.main()
