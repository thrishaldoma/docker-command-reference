import http.client
import threading
import unittest
from server import Handler, LINES, COMMANDS, FLAGS, EXAMPLES, ThreadingHTTPServer
from scripts.generate_reference import options, option_templates


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
        for line in LINES:
            self.assertRegex(line, r"^docker(?: .+)? - \S.+$")
        for line in COMMANDS:
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
        self.assertIn("docker compose up - Create and start containers", body.splitlines())
        self.assertIn("docker compose up -d - Start", body)
        self.assertTrue(all(line.startswith("docker compose up ") for line in body.splitlines()))
        status, _, body = self.request("/search?q=VOLUME")
        self.assertEqual(status, 200)
        self.assertTrue(all("volume" in line.lower() for line in body.splitlines()))

    def test_practical_examples_and_flag_collections(self):
        self.assertGreater(len(EXAMPLES), 100)
        self.assertGreater(len(FLAGS), 1000)
        self.assertTrue(LINES[0].startswith("docker run -d nginx - "))
        for endpoint, expected in (("/commands", COMMANDS), ("/flags", FLAGS), ("/examples", EXAMPLES)):
            status, _, body = self.request(endpoint)
            self.assertEqual(status, 200)
            self.assertEqual(body.splitlines(), expected)
        status, _, body = self.request("/run")
        self.assertEqual(status, 200)
        self.assertIn("docker run -d nginx - Run Nginx in detached mode", body)
        self.assertIn("docker run -p 8080:80 nginx - Publish host port 8080 to container port 80", body)
        self.assertIn("docker run -d - Run container in background and print container ID", body)
        self.assertIn("docker run --detach - Run container in background and print container ID", body)
        self.assertIn("docker run -p <list> - Publish", body)
        self.assertIn("docker run -P - Publish all exposed ports", body)
        self.assertEqual(self.request("/examples/run")[2].splitlines(),
                         [line for line in EXAMPLES if line.startswith("docker run ")])
        flags = self.request("/flags/compose/up")[2]
        self.assertIn("docker compose up --detach - ", flags)
        self.assertNotIn("docker run ", flags)
        self.assertTrue(all("-p" in line.lower() for line in self.request("/search?q=-p")[2].splitlines()))

    def test_rejections_and_health(self):
        self.assertEqual(self.request(ua="Mozilla/5.0")[0], 403)
        self.assertEqual(self.request(ua="")[0], 403)
        self.assertEqual(self.request("/missing")[0], 404)
        self.assertEqual(self.request("/search?q=")[0], 400)
        self.assertEqual(self.request(method="POST")[0], 405)
        self.assertEqual(self.request("/healthz")[2], "ok\n")
        self.assertEqual(self.request(method="HEAD")[2], "")


class FlagParserTests(unittest.TestCase):
    def test_wrapping_aliases_and_command_local_meaning(self):
        help_text = """Usage: docker run [OPTIONS] IMAGE

Options:
  -d, --detach             Run container in background and
                            print container ID
  -p, --publish list       Publish ports to the host
  -P, --publish-all        Publish all exposed ports
      --sig-proxy          Proxy signals (default true)

Examples:
  docker run -d nginx
"""
        parsed = list(options(help_text))
        self.assertEqual(len(parsed), 4)
        self.assertEqual(parsed[0], ("-d, --detach", "Run container in background and print container ID"))
        self.assertEqual(list(option_templates("docker run", parsed[1][0])),
                         ["docker run -p <list>", "docker run --publish <list>"])
        self.assertEqual(list(option_templates("docker run", parsed[2][0])),
                         ["docker run -P", "docker run --publish-all"])
        self.assertEqual(list(option_templates("docker agent new", "--model docker agent setup")),
                         ["docker agent new --model <value>"])


if __name__ == "__main__":
    unittest.main()
