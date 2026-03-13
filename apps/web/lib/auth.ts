import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import type { NextAuthConfig } from "next-auth";

declare module "next-auth" {
  interface Session {
    accessToken?: string;
    user: {
      id: string;
      login: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
    };
  }
}

export const authConfig: NextAuthConfig = {
  providers: [
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: "read:user user:email repo",
        },
      },
    }),
  ],
  callbacks: {
    async jwt({ token, account, profile }) {
      if (account) {
        token.accessToken = account.access_token;
        token.login = (profile as Record<string, unknown>)?.login;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string;
      if (session.user) {
        session.user.id = token.sub as string;
        session.user.login = token.login as string;
      }
      return session;
    },
  },
  pages: {
    signIn: "/auth/signin",
  },
};

export const { handlers, auth, signIn, signOut } = NextAuth(authConfig);
