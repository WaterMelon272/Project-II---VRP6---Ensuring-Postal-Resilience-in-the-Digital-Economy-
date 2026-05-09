#include <bits/stdc++.h>
using namespace std;

const int INF = 1e9;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k, q;
    cin >> n >> k >> q;

    vector<int> d(n);
    for (int i = 0; i < n; i++) cin >> d[i];

    vector<vector<int>> c(n + 1, vector<int>(n + 1));
    for (int i = 0; i <= n; i++)
        for (int j = 0; j <= n; j++)
            cin >> c[i][j];

    int N = 1 << n;
    vector<int> load(N, 0);

    for (int m = 1; m < N; m++) {
        int b = __builtin_ctz(m);
        load[m] = load[m ^ (1 << b)] + d[b];
    }

    vector<int> cost(N, INF);
    cost[0] = 0;
    vector<vector<int>> dp(N, vector<int>(n, INF));

    for (int i = 0; i < n; i++) {
        int m = 1 << i;
        dp[m][i] = c[0][i + 1];
    }

    for (int m = 1; m < N; m++) {
        for (int last = 0; last < n; last++) {
            if (!(m & (1 << last))) continue;
            int cur = dp[m][last];
            if (cur >= INF) continue;
            int rem = (N - 1) ^ m;
            for (int nxt = rem; nxt; nxt &= (nxt - 1)) {
                int j = __builtin_ctz(nxt);
                int nm = m | (1 << j);
                int val = cur + c[last + 1][j + 1];
                if (val < dp[nm][j]) dp[nm][j] = val;
            }
        }
    }

    for (int m = 1; m < N; m++) {
        if (load[m] > q) continue;
        int best = INF;
        for (int last = 0; last < n; last++) {
            if (!(m & (1 << last))) continue;
            int val = dp[m][last];
            if (val >= INF) continue;
            val += c[last + 1][0];
            best = min(best, val);
        }
        cost[m] = best;
    }


    vector<vector<int>> f(k + 1, vector<int>(N, INF));
    f[0][0] = 0;

    for (int t = 1; t <= k; t++) {
        for (int m = 0; m < N; m++) {
            if (f[t - 1][m] == INF) continue;
            int rem = (N - 1) ^ m;
            for (int s = rem; s; s = (s - 1) & rem) {
                if (cost[s] >= INF) continue;
                int nm = m | s;
                int val = f[t - 1][m] + cost[s];
                if (val < f[t][nm]) f[t][nm] = val;
            }
            f[t][m] = min(f[t][m], f[t - 1][m]);
        }
    }

    int full = N - 1;
    int ans = INF;
    for (int t = 1; t <= k; t++) ans = min(ans, f[t][full]);
    cout << (ans >= INF ? -1 : ans) << "\n";

    return 0;
}