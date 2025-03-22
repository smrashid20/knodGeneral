package jiang719;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;

import com.github.javadocparser.TokenMgrError;
import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseProblemException;
import com.github.javaparser.Range;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.PackageDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.comments.Comment;
import com.github.javaparser.ast.expr.AnnotationExpr;
import com.github.javaparser.ast.expr.Name;


public class MyParser {
	
	public static JavaParser parser = new JavaParser();
	
	public static Node parseMethodDeclaration(String code) {
        try {
            System.out.println("Parsing method declaration...");
            Node root = parser.parseMethodDeclaration(code).getResult().orElse(null);

            if (root == null) {
                System.err.println("Parsing failed: No result returned.");
                return null;
            }

            System.out.println("Successfully parsed method. Removing comments and annotations...");
            MyParser.removeComments(root);
            MyParser.removeAnnotation(root);

            System.out.println("Final parsed method node: " + root.toString());
            return root;
        } catch (ParseProblemException e) {
            System.err.println("Error: Failed to parse method declaration - " + e.getMessage());
            return null;
        } catch (Exception e) {
            System.err.println("Unexpected error during method parsing: " + e.getMessage());
            return null;
        }
    }
	
	public static CompilationUnit parseFile(String filename) throws FileNotFoundException {
        try {
            System.out.println("Parsing file: " + filename);
            Node root = parser.parse(new File(filename)).getResult().orElse(null);

            if (root == null) {
                System.err.println("Parsing failed: No result returned.");
                return null;
            }

            System.out.println("Successfully parsed file. Removing comments and annotations...");
            MyParser.removeComments(root);
            MyParser.removeAnnotation(root);

            System.out.println("Final parsed compilation unit: " + root.toString());
            return (CompilationUnit) root;
        } catch (ParseProblemException e) {
            System.err.println("Parsing error in file: " + filename + " - " + e.getMessage());
            return null;
        } catch (Exception e) {
            System.err.println("Unexpected error while parsing file: " + filename + " - " + e.getMessage());
            return null;
        }
    }
	
	public static CompilationUnit parseFile(File file) throws com.github.javadocparser.ParseException {
        try {
            System.out.println("Parsing file: " + file.getAbsolutePath());
            Node root = parser.parse(file).getResult().orElse(null);

            if (root == null) {
                System.err.println("Parsing failed: No result returned.");
                return null;
            }

            System.out.println("Successfully parsed file. Removing comments and annotations...");
            MyParser.removeComments(root);
            MyParser.removeAnnotation(root);

            System.out.println("Final parsed compilation unit: " + root.toString());
            return (CompilationUnit) root;
        } catch (TokenMgrError e) {
            System.err.println("Token manager error while parsing file: " + file.getAbsolutePath() + " - " + e.getMessage());
            return null;
        } catch (Exception e) {
            System.err.println("Unexpected error while parsing file: " + file.getAbsolutePath() + " - " + e.getMessage());
            return null;
        }
    }
	
	public static boolean containLines(Node node, int beginline, int endline, String subnodecode) {
        if (!node.getRange().isPresent()) {
            System.out.println("[containLines] Node has no range. Skipping.");
            return false;
        }

        Range noderange = node.getRange().get();
        System.out.println("[containLines] Checking node from line " + noderange.begin.line + " to " + noderange.end.line +
                " against target lines " + beginline + " to " + endline);

        if (noderange.begin.line > beginline || noderange.end.line < endline) {
            System.out.println("[containLines] Node is outside the target line range.");
            return false;
        }

        String nodestring = node.toString().replaceAll("\\s+", "");
        String subnodestring = subnodecode.replaceAll("\\s+", "");
        boolean contains = nodestring.contains(subnodestring);

        System.out.println("[containLines] Code match result: " + contains);
        return contains;
    }

    public static boolean containLines(Node node, String subnodecode) {
        if (!node.getRange().isPresent()) {
            System.out.println("[containLines(no-line-check)] Node has no range. Skipping.");
            return false;
        }

        String nodestring = node.toString().replaceAll("\\s+", "");
        String subnodestring = subnodecode.replaceAll("\\s+", "");
        boolean contains = nodestring.contains(subnodestring);

        System.out.println("[containLines(no-line-check)] Checking if node contains subcode -> Result: " + contains);
        return contains;
    }

    public static boolean containedByLines(Node node, int beginline, int endline, String code) {
        if (!node.getRange().isPresent()) {
            System.out.println("[containedByLines] Node has no range. Skipping.");
            return false;
        }

        Range noderange = node.getRange().get();
        System.out.println("[containedByLines] Checking if node from line " + noderange.begin.line + " to " + noderange.end.line +
                " is fully within target lines " + beginline + " to " + endline);

        if (noderange.begin.line < beginline || noderange.end.line > endline) {
            System.out.println("[containedByLines] Node is outside the allowed range.");
            return false;
        }

        String nodestring = node.toString().replaceAll("\\s+", "");
        String string = code.replaceAll("\\s+", "");
        boolean contains = string.contains(nodestring);

        System.out.println("[containedByLines] Is node content contained in code snippet? " + contains);
        return contains;
    }

	
	private static void findSubNode_(Node node, int beginline, int endline, String subnodecode, Node[] subnode) {
        System.out.println("[findSubNode_] Visiting node: " + node.getClass().getSimpleName() +
                           " at lines: " + (node.getRange().isPresent() ? node.getRange().get() : "unknown"));

        if (containLines(node, beginline, endline, subnodecode)) {
            System.out.println("[findSubNode_] Match found! Assigning node: " + node.getClass().getSimpleName());
            subnode[0] = node;

            for (Node child : node.getChildNodes()) {
                findSubNode_(child, beginline, endline, subnodecode, subnode);
            }
        }
    }

    public static Node findSubNode(Node node, int beginline, int endline, String subnodecode) {
        System.out.println("[findSubNode] Searching for subnode in lines " + beginline + " to " + endline);
        Node[] subnode = new Node[1];
        findSubNode_(node, beginline, endline, subnodecode, subnode);
        if (subnode[0] != null) {
            System.out.println("[findSubNode] Final match: " + subnode[0].getClass().getSimpleName() +
                               " at " + subnode[0].getRange().get());
        } else {
            System.out.println("[findSubNode] No matching subnode found.");
        }
        return subnode[0];
    }

	
	public static void removeComments(Node node) {
        if (node == null) return;

        if (node.getComment().isPresent()) {
            System.out.println("[removeComments] Removing comment from node: " + node.getClass().getSimpleName());
            node.removeComment();
        }

        List<Comment> comments = node.getAllContainedComments();
        if (!comments.isEmpty()) {
            System.out.println("[removeComments] Removing " + comments.size() + " contained comments.");
        }

        for (Comment comment : comments) {
            comment.remove();
        }

        for (Node child : node.getChildNodes()) {
            removeComments(child);
        }
    }

	
	public static void removeAnnotation(Node node) {
        List<AnnotationExpr> annotations = node.findAll(AnnotationExpr.class);
        if (!annotations.isEmpty()) {
            System.out.println("[removeAnnotation] Removing " + annotations.size() + " annotations.");
        }

        for (Node annotation : annotations) {
            System.out.println("[removeAnnotation] Removing annotation: " + annotation);
            annotation.removeForced();
        }
    }

	
	public static MyNode calculateDepth(Node node, int depth) {
        System.out.println("[calculateDepth] Depth: " + depth + " - Node: " + node.getClass().getSimpleName());
        MyNode mynode = new MyNode(node, depth);

        for (Node child : node.getChildNodes()) {
            MyNode mychild = calculateDepth(child, depth + 1);
            mynode.addChild(mychild);
        }

        return mynode;
    }

	
	public static ArrayList<String> analysisImports(MyNode myroot){
        System.out.println("[analysisImports] Starting import analysis...");
        ArrayList<String> imports = new ArrayList<String>();
        ArrayList<MyNode> dfs = myroot.DFS();
        for (MyNode mynode : dfs) {
            if (mynode.classEquals(ImportDeclaration.class)) {
                String importValue = mynode.getChildrenByTpye(Name.class).get(0).getValue();
                System.out.println("[analysisImports] Found import: " + importValue);
                imports.add(importValue);
            }
        }
        System.out.println("[analysisImports] Total imports found: " + imports.size());
        return imports;
    }

    public static String analysisPackages(MyNode myroot) {
        System.out.println("[analysisPackages] Starting package analysis...");
        ArrayList<MyNode> dfs = myroot.DFS();
        for (MyNode mynode : dfs) {
            if (mynode.classEquals(PackageDeclaration.class)) {
                String packageName = mynode.getChildrenByTpye(Name.class).get(0).getValue();
                System.out.println("[analysisPackages] Found package: " + packageName);
                return packageName;
            }
        }
        System.out.println("[analysisPackages] No package declaration found.");
        return null;
    }

    public static void findCoveringBuggyNode_(Node node, String code, int beginline, int endline, Node[] subnode) {
        System.out.println("[findCoveringBuggyNode_] Visiting node: " + node.getClass().getSimpleName() +
                           " at lines: " + (node.getRange().isPresent() ? node.getRange().get() : "unknown"));
        if (containLines(node, beginline, endline, code)) {
            System.out.println("[findCoveringBuggyNode_] Node contains buggy code. Setting candidate.");
            subnode[0] = node;
            List<Node> childs = node.getChildNodes();
            for (Node child : childs) {
                findCoveringBuggyNode_(child, code, beginline, endline, subnode);
            }
        }
    }

    public static Node findCoveringBuggyNode(Node context, String code, int beginline, int endline) throws IOException {
        System.out.println("[findCoveringBuggyNode] Searching for covering node in lines " + beginline + "-" + endline);
        Node[] subnode = {null};
        findCoveringBuggyNode_(context, code, beginline, endline, subnode);
        if (subnode[0] != null) {
            System.out.println("[findCoveringBuggyNode] Found covering node: " + subnode[0].getClass().getSimpleName());
        } else {
            System.out.println("[findCoveringBuggyNode] No covering node found.");
        }
        return subnode[0];
    }

    public static void findCoveringBuggyNode_(Node node, ArrayList<Node> subnodes, Node[] result) {
        if (!node.getRange().isPresent()) return;
        boolean covering = true;
        for (Node subnode : subnodes) {
            Range range = subnode.getRange().get();
            if (!node.getRange().get().contains(range)) {
                covering = false;
                break;
            }
        }
        if (covering) {
            System.out.println("[findCoveringBuggyNode_(multi)] Node " + node.getClass().getSimpleName() +
                               " covers all subnodes.");
            result[0] = node;
            for (Node child : node.getChildNodes()) {
                findCoveringBuggyNode_(child, subnodes, result);
            }
        }
    }

    public static Node findCoveringBuggyNode(Node context, ArrayList<Node> subnodes) {
        System.out.println("[findCoveringBuggyNode(multi)] Finding node that covers all subnodes...");
        Node[] result = {null};
        findCoveringBuggyNode_(context, subnodes, result);
        if (result[0] != null) {
            System.out.println("[findCoveringBuggyNode(multi)] Found covering node: " + result[0].getClass().getSimpleName());
        } else {
            System.out.println("[findCoveringBuggyNode(multi)] No covering node found.");
        }
        return result[0];
    }

    public static void findCoveredBuggyNode_(Node node, String code, int beginline, int endline, ArrayList<Node> subnodes) {
        if (containedByLines(node, beginline, endline, code)) {
            System.out.println("[findCoveredBuggyNode_] Node " + node.getClass().getSimpleName() +
                               " is covered by given range. Adding to result.");
            subnodes.add(node);
        } else {
            for (Node child : node.getChildNodes()) {
                findCoveredBuggyNode_(child, code, beginline, endline, subnodes);
            }
        }
    }
	
    public static void findCoveredBuggyNode_(Node node, int startLine, int startColumn, int endLine, int endColumn, ArrayList<Node> subnodes) {
        if (!node.getRange().isPresent()) {
            System.out.println("[findCoveredBuggyNode_] Node has no range. Skipping...");
            return;
        }

        Range range = node.getRange().get();
        System.out.println("[findCoveredBuggyNode_] Checking node: " + node.getClass().getSimpleName() +
                           " Range: " + range);

        boolean covered = false;
        if (range.begin.line > startLine || (range.begin.line == startLine && range.begin.column >= startColumn)) {
            if (range.end.line < endLine || (range.end.line == endLine && range.end.column <= endColumn)) {
                covered = true;
            }
        }

        if (covered) {
            System.out.println("[findCoveredBuggyNode_] Node is covered. Adding: " + node.getClass().getSimpleName());
            subnodes.add(node);
        } else {
            for (Node child : node.getChildNodes()) {
                findCoveredBuggyNode_(child, startLine, startColumn, endLine, endColumn, subnodes);
            }
        }
    }

    public static ArrayList<Node> findCoveredBuggyNode(Node context, int startLine, int startColumn, int endLine, int endColumn) {
            System.out.println("[findCoveredBuggyNode] Searching for nodes covered by range: " +
                               startLine + ":" + startColumn + " to " + endLine + ":" + endColumn);
            ArrayList<Node> subnodes = new ArrayList<Node>();
            findCoveredBuggyNode_(context, startLine, startColumn, endLine, endColumn, subnodes);
            System.out.println("[findCoveredBuggyNode] Total covered nodes found: " + subnodes.size());
            return subnodes;
        }

        public static ArrayList<Node> findCoveredBuggyNode(Node context, int beginline, int endline, String code) {
            System.out.println("[findCoveredBuggyNode (code)] Searching for nodes within lines: " + beginline + " to " + endline);
            ArrayList<Node> subnodes = new ArrayList<Node>();
            findCoveredBuggyNode_(context, code, beginline, endline, subnodes);
            System.out.println("[findCoveredBuggyNode (code)] Total covered nodes found: " + subnodes.size());
            return subnodes;
        }

        public static HashMap<Node, Integer> findBuggyNodeIndex(Node context, ArrayList<Node> buggynodes) {
            System.out.println("[findBuggyNodeIndex] Starting index lookup for " + buggynodes.size() + " buggy nodes.");
            HashMap<Node, Integer> indices = new HashMap<Node, Integer>();

            for (Node buggynode : buggynodes) {
                String buggycode = buggynode.toString().trim();
                System.out.println("[findBuggyNodeIndex] Looking for node with code: " + buggycode.replaceAll("\n", " "));
                HashMap<String, Node> range2nodes = new HashMap<>();
                MyNode mycontext = calculateDepth(context, 0);

                for (MyNode mynode : mycontext.DFS()) {
                    String nodecode = mynode.node.toString().trim();
                    if (nodecode.equals(buggycode)) {
                        String rangeStr = mynode.node.getRange().isPresent() ? mynode.node.getRange().get().toString() : "unknown";
                        range2nodes.put(rangeStr, mynode.node);
                        System.out.println("[findBuggyNodeIndex] Candidate match found at range: " + rangeStr);
                    }
                }

                ArrayList<Node> samenodes = new ArrayList<>(range2nodes.values());
                Collections.sort(samenodes, new Comparator<Node>() {
                    public int compare(Node n1, Node n2) {
                        Range r1 = n1.getRange().get();
                        Range r2 = n2.getRange().get();
                        if (r1.begin.line == r2.begin.line) {
                            if (r1.begin.column == r2.begin.column) {
                                if (r1.end.line == r2.end.line)
                                    return r1.end.column - r2.end.column;
                                return r1.end.line - r2.end.line;
                            }
                            return r1.begin.column - r2.begin.column;
                        }
                        return r1.begin.line - r2.begin.line;
                    }
                });

                for (int i = 0; i < samenodes.size(); i++) {
                    if (samenodes.get(i).toString().equals(buggynode.toString()) &&
                        samenodes.get(i).getRange().get().equals(buggynode.getRange().get())) {
                        System.out.println("[findBuggyNodeIndex] Final match at index " + i);
                        indices.put(buggynode, i);
                        break;
                    }
                }
            }

            System.out.println("[findBuggyNodeIndex] Index lookup complete. Total matches: " + indices.size());
            return indices;
        }


    public static ArrayList<String> findContextBeforeAfter(String filePath, Node context, int startLine, int startColumn, int endLine, int endColumn) throws IOException {
        System.out.println("[findContextBeforeAfter] Extracting context from file: " + filePath);
        System.out.println("[findContextBeforeAfter] Range - Start: " + startLine + ":" + startColumn + ", End: " + endLine + ":" + endColumn);

        ArrayList<String> contextBeforeAfter = new ArrayList<String>();
        BufferedReader br = new BufferedReader(new FileReader(new File(filePath)));
        String line;
        int cnt = 0;
        String contextBefore = "", contextAfter = "";

        while ((line = br.readLine()) != null) {
            cnt += 1;
            if (cnt < context.getRange().get().begin.line || cnt > context.getRange().get().end.line)
                continue;

            if (cnt < startLine) {
                contextBefore += line;
                continue;
            }

            if (cnt == startLine) {
                for (int i = 0; i < line.length(); i += 1) {
                    if (i + 1 < startColumn)
                        contextBefore += line.substring(i, i + 1);
                }
            }

            if (cnt == endLine) {
                for (int i = 0; i < line.length(); i += 1) {
                    if (i + 1 > endColumn)
                        contextAfter += line.substring(i, i + 1);
                }
            }

            if (cnt > endLine) {
                contextAfter += line;
            }
        }
        br.close();

        System.out.println("[findContextBeforeAfter] Context before: " + contextBefore.replaceAll("\\s+", ""));
        System.out.println("[findContextBeforeAfter] Context after: " + contextAfter.replaceAll("\\s+", ""));

        contextBeforeAfter.add(contextBefore);
        contextBeforeAfter.add(contextAfter);
        return contextBeforeAfter;
    }

    public static ArrayList<Integer> findContextRange(String filePath, Node context, String contextBefore, String contextAfter) throws IOException {
        System.out.println("[findContextRange] Searching for context range in file: " + filePath);

        BufferedReader br = new BufferedReader(new FileReader(new File(filePath)));
        String line;
        String content = "";
        int cnt = 0;

        while ((line = br.readLine()) != null) {
            cnt += 1;
            if (cnt < context.getRange().get().begin.line || cnt > context.getRange().get().end.line)
                continue;
            content += line;
        }
        br.close();

        ArrayList<Integer> range = new ArrayList<Integer>();
        br = new BufferedReader(new FileReader(new File(filePath)));
        cnt = 0;
        String before = "", after = content;
        int beforeLine = -1, beforeColumn = -1, afterLine = -1, afterColumn = -1;
        contextBefore = contextBefore.replaceAll("\\s+", "");
        contextAfter = contextAfter.replaceAll("\\s+", "");

        while ((line = br.readLine()) != null) {
            cnt += 1;
            if (cnt < context.getRange().get().begin.line || cnt > context.getRange().get().end.line)
                continue;

            if (beforeLine == -1) {
                for (int i = 0; i < line.length(); i += 1) {
                    before += line.substring(i, i + 1);
                    if (before.replaceAll("\\s+", "").equals(contextBefore)) {
                        beforeLine = cnt;
                        beforeColumn = i + 1;
                        System.out.println("[findContextRange] Found contextBefore at line " + beforeLine + ", column " + beforeColumn);
                        break;
                    }
                }
            }

            if (afterLine == -1) {
                for (int i = 0; i < line.length(); i += 1) {
                    if (after.replaceAll("\\s+", "").equals(contextAfter)) {
                        afterLine = cnt;
                        afterColumn = i + 1;
                        System.out.println("[findContextRange] Found contextAfter at line " + afterLine + ", column " + afterColumn);
                        break;
                    }
                    after = after.substring(1);
                }
            }
        }
        br.close();

        range.add(beforeLine);
        range.add(beforeColumn);
        range.add(afterLine);
        range.add(afterColumn);

        System.out.println("[findContextRange] Final range: " + range);
        return range;
    }

	
	public static void findContext_(Node node, int beginline, int endline, String code, Node[] subnode) {
		if (containLines(node, beginline, endline, code)) {
			if (node.getClass().equals(MethodDeclaration.class) || node.getClass().equals(ConstructorDeclaration.class))
				subnode[1] = node;
			subnode[0] = node;
			List<Node> childs = node.getChildNodes();
			for (Node child : childs) {
				findContext_(child, beginline, endline, code, subnode);
			}
		}
	}
	
    public static Node findContextNode(Node node, int beginline, int endline, String code) {
        System.out.println("[findContextNode] Searching for context node between lines " + beginline + " and " + endline);
        Node[] subnode = {null, null};
        findContext_(node, beginline, endline, code, subnode);
        if (subnode[1] != null) {
            System.out.println("[findContextNode] Found context node: " + subnode[1].getClass().getSimpleName());
        } else {
            System.out.println("[findContextNode] No context node found.");
        }
        return subnode[1];
    }

    public static Node findContextNode(String filepath, int beginline, int endline) throws IOException {
        System.out.println("[findContextNode(file)] Reading code from file: " + filepath);
        BufferedReader br = new BufferedReader(new FileReader(new File(filepath)));
        String line;
        int cnt = 0;
        String code = "";
        while ((line = br.readLine()) != null) {
            cnt += 1;
            if (beginline <= cnt && cnt < endline)
                code += line.trim() + " ";
            if (cnt >= endline)
                break;
        }
        br.close();
        code = code.trim();
        try {
            System.out.println("[findContextNode(file)] Parsed code snippet: " + code.replaceAll("\\s+", ""));
            Node root = MyParser.parseFile(filepath);
            return findContextNode(root, beginline, endline, code);
        } catch (TokenMgrError e) {
            System.out.println("[findContextNode(file)] TokenMgrError: " + e.getMessage());
            return null;
        }
    }

    public static String findContext(String filepath, int beginline, int endline) throws IOException {
        System.out.println("[findContext] Finding context string from lines " + beginline + " to " + endline);
        BufferedReader br = new BufferedReader(new FileReader(new File(filepath)));
        String line;
        int cnt = 0;
        String code = "";
        while ((line = br.readLine()) != null) {
            cnt += 1;
            if (beginline <= cnt && cnt < endline)
                code += line.trim() + " ";
            if (cnt >= endline)
                break;
        }
        br.close();
        code = code.trim();
        try {
            Node root = MyParser.parseFile(filepath);
            Node context = findContextNode(root, beginline, endline - 1, code);
            if (context != null) {
                System.out.println("[findContext] Found context node: " + context.getClass().getSimpleName());
                return context.toString();
            } else {
                System.out.println("[findContext] No context found.");
                return "";
            }
        } catch (TokenMgrError e) {
            System.out.println("[findContext] TokenMgrError: " + e.getMessage());
            return "";
        }
    }

    public static void main(String[] args) throws Exception {
        String filepath = "D:\\java-eclipse-workspace\\deeprepair-javaparser\\src\\test\\java\\jiang719\\test\\Test1.java";
        System.out.println("[main] Parsing file: " + filepath);
        Node root = MyParser.parseFile(filepath);

        if (root == null) {
            System.out.println("[main] Parsing failed.");
            return;
        }

        System.out.println("[main] Traversing and printing AST...");
        for (MyNode node : MyParser.calculateDepth(root, 0).DFS()) {
            System.out.println(node);
        }
        System.out.println("[main] AST traversal complete.");
    }

}
